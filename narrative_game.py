from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class GameState:
    """Tracks the player's current standing and notable decisions."""

    trust: int = 0
    hope: int = 0
    supplies: int = 3
    log: List[str] = field(default_factory=list)

    def apply(self, effects: Dict[str, int]) -> None:
        for attr, delta in effects.items():
            if hasattr(self, attr):
                value = getattr(self, attr)
                setattr(self, attr, value + delta)

    def summary(self) -> str:
        return (
            f"Trust: {self.trust}, Hope: {self.hope}, Supplies: {self.supplies}\n"
            + "Decisions: "
            + "; ".join(self.log)
        )


@dataclass
class Choice:
    description: str
    consequence: str
    next_scene: Optional[str]
    effects: Dict[str, int] = field(default_factory=dict)


@dataclass
class Scene:
    title: str
    narrative: str
    choices: List[Choice]
    endpoint: Optional[str] = None


class NarrativeGame:
    def __init__(self) -> None:
        self.state = GameState()
        self.scenes = self._build_story()

    def _build_story(self) -> Dict[str, Scene]:
        return {
            "start": Scene(
                title="Train Through the Wastes",
                narrative=(
                    "A battered train crawls through a scarred coastline. The crew speaks in "
                    "whispers of dwindling food and the promise of a safe haven down the line."
                ),
                choices=[
                    Choice(
                        description="Search the freight cars for hidden rations.",
                        consequence="You sift through crates while eyes follow your every move.",
                        next_scene="missing_rations",
                        effects={"supplies": 1, "trust": -1},
                    ),
                    Choice(
                        description="Check the emergency radio for any signal.",
                        consequence="A cracked voice bleeds through the static, begging for a ride.",
                        next_scene="distress_call",
                        effects={"hope": 1},
                    ),
                    Choice(
                        description="Talk to the conductor about the mood on board.",
                        consequence=(
                            "The conductor shares fears about deserters and slips you a folded note."
                        ),
                        next_scene="conductor_confides",
                        effects={"trust": 1},
                    ),
                ],
            ),
            "missing_rations": Scene(
                title="Missing Rations",
                narrative=(
                    "A stash of cans is gone. The crew looks to you, waiting for judgment while "
                    "the train shudders over rusted tracks."
                ),
                choices=[
                    Choice(
                        description="Share half of your find to calm everyone.",
                        consequence="Suspicion eases as hands pass food down the car.",
                        next_scene="distress_call",
                        effects={"trust": 1, "supplies": -1, "hope": 1},
                    ),
                    Choice(
                        description="Hide the cans and say nothing for now.",
                        consequence="You stash them away. A crew member notices and scowls.",
                        next_scene="storm",
                        effects={"trust": -2, "hope": -1},
                    ),
                ],
            ),
            "distress_call": Scene(
                title="Distress Call",
                narrative=(
                    "The radio bursts alive. A caravan trapped on a flooded bridge pleads for transport."
                ),
                choices=[
                    Choice(
                        description="Answer and divert to the bridge.",
                        consequence="The train slows as you prepare to pull strangers aboard.",
                        next_scene="bridge_meet",
                        effects={"trust": 1, "hope": 1},
                    ),
                    Choice(
                        description="Ignore it and stay on schedule.",
                        consequence="You cut the signal. The car grows colder with the silence.",
                        next_scene="storm",
                        effects={"hope": -1},
                    ),
                ],
            ),
            "conductor_confides": Scene(
                title="Conductor's Note",
                narrative=(
                    "The note lists passengers who have been stealing supplies. The conductor asks for "
                    "your discretion as storm clouds gather ahead."
                ),
                choices=[
                    Choice(
                        description="Confront the accused with the conductor at your side.",
                        consequence="The accused deny it but agree to make amends if you help the bridge caravan.",
                        next_scene="bridge_meet",
                        effects={"trust": 2, "hope": 1},
                    ),
                    Choice(
                        description="Keep the secret and focus on beating the storm.",
                        consequence="The conductor frowns, feeling alone with the burden.",
                        next_scene="storm",
                        effects={"trust": -1},
                    ),
                ],
            ),
            "bridge_meet": Scene(
                title="Bridge Caravan",
                narrative=(
                    "At the flooded bridge, desperate survivors cling to their gear. Space is tight and the "
                    "crew eyes the newcomers warily."
                ),
                choices=[
                    Choice(
                        description="Invite them aboard and split the remaining supplies.",
                        consequence="Hands clasp, forming a shaky convoy toward the refuge.",
                        next_scene=None,
                        effects={"trust": 2, "hope": 2, "supplies": -1},
                    ),
                    Choice(
                        description="Keep the train sealed unless they trade weapons.",
                        consequence="A tense standoff ends with the caravan leaving you behind, bitter and armed.",
                        next_scene=None,
                        effects={"trust": -2, "hope": -1},
                    ),
                ],
                endpoint="The Convoy Forms",
            ),
            "storm": Scene(
                title="Storm Front",
                narrative=(
                    "Lightning rips across the horizon. The rails ahead are slick, and the cars groan under the strain."
                ),
                choices=[
                    Choice(
                        description="Secure every car together and brave the storm as a group.",
                        consequence="You lash the couplings tight. The crew works in rhythm, voices rising over the wind.",
                        next_scene=None,
                        effects={"trust": 1, "hope": 1},
                    ),
                    Choice(
                        description="Detach the heavy caboose to move faster alone.",
                        consequence="You cut the line. Shouts fade behind you as the train lurches forward.",
                        next_scene=None,
                        effects={"trust": -3, "hope": -2, "supplies": -2},
                    ),
                ],
                endpoint="Riding Out the Storm",
            ),
        }

    def play(self, *, scripted_choices: Optional[List[int]] = None) -> str:
        scene_key = "start"
        scripted_index = 0

        while True:
            scene = self.scenes[scene_key]
            self._display_scene(scene)

            if scene.endpoint and not scene.choices:
                return scene.endpoint

            choice_index = self._get_choice_index(scene, scripted_choices, scripted_index)
            if scripted_choices is not None:
                scripted_index += 1

            choice = scene.choices[choice_index]
            self.state.apply(choice.effects)
            self.state.log.append(choice.consequence)

            if choice.next_scene is None:
                return scene.endpoint or "Journey Complete"

            scene_key = choice.next_scene

    def _display_scene(self, scene: Scene) -> None:
        print(f"\n== {scene.title} ==")
        print(scene.narrative)

        for i, choice in enumerate(scene.choices, start=1):
            print(f"  {i}. {choice.description}")

    def _get_choice_index(
        self, scene: Scene, scripted_choices: Optional[List[int]], scripted_index: int
    ) -> int:
        if scripted_choices is not None and scripted_index < len(scripted_choices):
            selection = scripted_choices[scripted_index]
            if 0 <= selection < len(scene.choices):
                return selection
            raise IndexError("Scripted choice index out of range.")

        while True:
            raw = input("Select a choice: ").strip()
            if raw.isdigit():
                selection = int(raw) - 1
                if 0 <= selection < len(scene.choices):
                    return selection
            print("Please enter a valid number.")

    def simulate_path(self, choices: List[int]) -> Dict[str, str]:
        self.state = GameState()
        ending = self.play(scripted_choices=choices)
        return {"ending": ending, "summary": self.state.summary()}


if __name__ == "__main__":
    game = NarrativeGame()
    final_ending = game.play()
    print("\nEpilogue:")
    print(game.state.summary())
    print(f"Ending: {final_ending}")
