# PROJECT-BRIEF — walker-TANK: one finished level

CSYE 7270 · Assignment 8 · Final project pitch
Stack: Godot 4.7.2 stable · GDScript · Forward+ · export target: **Windows desktop** · built with Claude Code on Windows 11.

## 1. What is it?

walker-TANK is a 2D top-down tank game in which you drive YunqiZ through a ruined brick battlefield and destroy three enemy tanks.
When the final project is done, it will be **a Windows desktop build of one finished level**: title screen, the battle, and a win or lose screen, plus a test report that a stranger can rerun with one command.

## 2. Why would anyone care?

It gives a player who likes simple 2D tank games a battlefield that shows what is happening in it.
In *全民坦克大战*, a 2D browser tank game on 7k7k that I played, as I remember it, cover could not be destroyed, firing had no effect, and a destroyed tank did not smoke.
In walker-TANK, which already exists at tag a7, cover breaks where the shell hits, YunqiZ flashes red when it is hit (enemy tanks flash white), and a badly hurt tank smokes more as its health drops.
I make no claim about players, sales or the market; I have not playtested with anyone but myself.

## 3. Who opens it, and what do they do?

Target role: **gameplay programmer**. Reader: a hiring manager or lead engineer.
In the first sixty seconds they unzip the build, double-click the .exe, see the title screen with the controls on it, press start, and are driving within a minute without reading anything.
In the next few minutes they can open TEST-REPORT.md and rerun the tests themselves.

## 4. What does it prove about me?

- **Shaders and materials:** a hit-flash shader and a brick surface shader I typed myself (a5); tests pass at 30, 60 and 144 fps.
- **Particle effects:** a cover-hit burst and health-driven damage smoke (a6).
- **Animation and state:** track dust and fire clips with pinned state tests (a7).
- **Profiling:** measured cost of each effect on an NVIDIA RTX 3060 Laptop GPU (a6: +0.023 ms and +0.077 ms GPU).
- **Verification habits:** headless tests, mutations that must fail the tests, human checks written down where no headless run can see, and Claude Code directed through CLAUDE.md and change briefs.

A reviewer could fairly conclude that I can add a feature to a Godot game and prove it works. The final project will add evidence that I can **finish** a game: a full loop in an exported build, tested outside the editor.

## 5. What is in, what is out, what comes first?

- **In:** one level, title screen, win and lose screens, the effects that already exist, a Windows export, a rerunnable test report.
- **Out:** no multiplayer, no save system, no second level.
- **First:** export the current game to a Windows .exe and play it from a clean folder to a win. I will know it ran from a capture of that run and a log file, recorded in TEST-REPORT.md with the commit it was built from.

## 6. What could sink it?

Every test and every measurement so far ran in the editor or headless, on one machine with an RTX 3060. The game has never been exported. Forward+ needs a GPU that supports Vulkan or Direct3D 12, so the build may fail or look wrong on a reviewer's laptop with integrated graphics, and an effect may behave differently in an exported build.
What I will do: export in the first week, run the build on a second machine, and if it fails, switch to the Compatibility renderer and recheck each shader and particle effect, logging what changed.
I am not choosing a web export, because it runs only on the Compatibility renderer.

## 7. Why this project?

It is a mix of showing off and learning.
**Shown, with evidence:** shaders, particles, animation, profiling and testing, all learned in this course and visible at tags a5, a6 and a7.
**New to me:** exporting a Godot game, making it run on a machine I do not control, and finishing a game from title screen to end screen.
I picked it because the parts exist one by one, and a recruiter cannot judge parts; they can judge a finished level.

---

## Exists today

| What | Where to see it |
|---|---|
| walker-TANK 2D game: YunqiZ, three enemy tanks, brick cover | tag a2 |
| Three Blender assets in a 3D scene, check 18/18 | tag a3, `scenes/asset_room_3d.tscn`, `tests/check_a3_assets.gd` |
| Hit-flash shader, brick surface shader, two materials | tag a5, `shaders/` |
| Cover-hit burst, damage smoke, GPU cost measured | tag a6, `effects/`, `tests/price_measure.gd` |
| Track dust and fire animation clips, state tests | tag a7, `animations/`, `tests/test_anim_states.gd` |

## Will exist

- Title screen and win/lose screens
- One level playable from start to end
- Windows desktop export, run on a second machine
- One-command test runner and a TEST-REPORT a stranger can rerun
- A log of what changed between the editor and the exported build
