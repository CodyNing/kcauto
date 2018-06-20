# kcauto-kai

**kcauto-kai** is a robust Kantai Collection automation tool. kcauto-kai and it's predecessor, [kancolle-auto](https://github.com/mrmin123/kancolle-auto), are proof-of-concepts in using [Sikuli](http://sikulix.com/) for vision-based automation to play Kantai Collection. They are exercises in automating large, convoluted, and complex game-playing logic. The primary logic of kcauto-kai is written in Jython 2.7, with a standalone browser interface for config generation written in React JavaScript.

kcauto-kai is not designed to be the fastest automation tool, but is instead robust, highly customizable, and relatively safe to use. Please read the Disclaimer below before use!

---

Please consider supporting the developer on [Patreon](https://www.patreon.com/mrmin123) or [MakerSupport](https://www.makersupport.com/mrmin123).

<a href="https://www.patreon.com/mrmin123"><img src="https://c5.patreon.com/external/logo/become_a_patron_button.png" width="130" /></a>

---

Please submit bugs and feature requests on the [kcauto-kai issue tracker](https://github.com/mrmin123/kcauto-kai/issues). Please make sure you are on the latest release of kcauto-kai and that the bug/feature has not been reported already before opening an issue on the tracker.

Join the [kcauto-kai Discord server](https://discord.gg/smAhRKw) for kcauto-kai news, updates, and discussion. For more general Kantai Collection discussion, please join the [sister Discord server](https://discord.gg/2tt5Der).


---

> ### Disclaimer

> kcauto-kai is meant for educational purposes only! Actual and prolonged usage of kcauto-kai may result in your account being banned. Remember that botting is against rules! The developer of kcauto-kai makes no guarantee that the end-user will not be caught and penalized for using kcauto-kai, and does not take any responsibility for any repercussions that befall the end-user. Non-stop expeditions and sorties increases the chances of being flagged and banned for botting.

> In addition, although unlikely, you may lose ships if you allow kcauto-kai to conduct combat sorties. While kcauto-kai has been painstakingly designed to reduce the chances of this happening, the developer of kcauto-kai does not take responsibility regarding loss of ships and/or resources. Any browser/viewer features that obscure parts of the game screen (such as subtitles) has the ability to hinder proper damage state detection, which may lead to loss of ships.

---

### Features

* Expedition Module &mdash; automate expeditions
  * Multiple expeditions per fleet
  * Event and non-event boss and node support expeditions
* PvP Module &mdash; automate PvP
  * Automatic diamond or line abreast formations against submarine-heavy opponents
* Combat Module &mdash; automate combat sorties
  * Choice between [Live and Legacy combat engines](https://github.com/mrmin123/kcauto-kai/wiki/Config:-Combat-section#engine)
* LBAS Module &mdash; automatic LBAS management
  * Automatic resupply, fatigue management, and node assignment
* Ship Switcher Module &mdash; automatic switching of ships based on specified criteria between combat sorties
* Fleet Switcher Module &mdash; automatic switching of fleet presets for PvP and combat sorties
* Quests Module &mdash; automatic quest management
* Repair & Resupply Modules &mdash; automatic resupply and repair of fleet ships
* Stats &mdash; keeps stats on various actions performed
* Scheduled and manual sleeping and pausing of individual modules or entire script
* Automatic catbomb and script recovery
* Browser/viewer-agnostic
* Random variations in navigation, timers, and click positions to combat bot detection
* Open-source codebase and no reporting or phoning home
* Hot-reload config files
* [Web interface](https://mrmin123.github.io/kcauto-kai/) to generate and modify config files


### Installation and Usage

1. Install [Java JRE 8](http://www.oracle.com/technetwork/java/javase/downloads/jre8-downloads-2133155.html)
2. Install the latest [SikuliX Nightly](https://raiman.github.io/SikuliX1/nightly.html) with option 1 (Pack 1) selected
3. Download kcauto-kai either by downloading the repo or cloning it
4. Set up kcauto-kai's config file using the [web interface](https://mrmin123.github.io/kcauto-kai/) or by opening the local copy of `docs/index.html` in a browser
5. Run Kantai Collection in your favorite browser or viewer
6. Run kcauto-kai using the command `java -jar <path_to_sikuli>/sikulix.jar -r <path_to_kcauto-kai>/kcauto-kai.sikuli` (replacing `<path_to_sikuli>` and `<path_to_kcauto-kai>` with the correct directories for your installs); you can also use the [RunCmd tab](https://mrmin123.github.io/kcauto-kai/#runcmd) of the web interface to help generate the command

### Updating

The preferred method of keeping kcauto-kai up to date is via git. This requires you have a working [git](https://git-scm.com/) installation, have cloned the kcauto-kai repository, and are running kcauto-kai off of said clone.

If you do have git and cloned the kcauto-kai repository, use one of the following command to update to the latest release (`master` version) of kcauto-kai:

* `git pull origin master` or `git pull`

If you do not have git but would still like to keep up with `master`, please use [this guide](https://github.com/KC3Kai/KC3Kai/wiki/Setup-development-build) for setting up tortoisegit, but with the clone URL changed to `https://github.com/mrmin123/kcauto-kai.git`

If you do not have git, tortoisegit, or a clone of the kcauto-kai repository, head to the [Releases page](https://github.com/mrmin123/kcauto-kai/releases) and download the latest tagged version. Overwrite your local kcauto-kai installation with the contents of the new release, taking care to first back up or not overwrite your config file. Note that your config file may need updating to be compatible with new releases.
