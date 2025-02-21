# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).


[Unreleased]

###Added

###Changed


###Fixed

[20250221.1]

###Added
- Added the ability to turn autoscaling of the y axis on and off, along with a textbox to allow the user to enter a fixed y-axis max in scientific notation
- Added this CHANGELOG.md file. Long overdue!
- Improved scan lineedit widget to allow the user to manually enter a scan number

###Changed
- Relaxed some constraints on additional peaks desired to obtain a better fit for "shoudlers".

###Fixed
- Fixed a minor error in the gaussian model equation used for fitting that could cause some large amplitude values to slightly underfit for each peak

