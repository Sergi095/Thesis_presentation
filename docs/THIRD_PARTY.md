# Third-party components

- **gym-pybullet-drones / DSLPIDControl and Crazyflie CF2X parameters**:
  https://github.com/utiasDSL/gym-pybullet-drones
  MIT, copyright (c) 2020 Jacopo Panerati. The JavaScript flight controller is an
  adaptation of the standard DSL controller, based on work at UTIAS' DSL by
  SiQi Zhou, James Xu, Tracy Du, Mario Vukosavljev, Calvin Ngan and Jingyuan Hou.
  The full [MIT license](licenses/gym-pybullet-drones.txt) is retained and shipped.
- **Ammo.js / Bullet**, supplied by the pinned `ammojs3` package:
  https://github.com/kripken/ammo.js and https://github.com/i12345/ammo.js
  zlib license; distributed as `vendor/ammo.LICENSE` with the site.
- **Three.js**: https://github.com/mrdoob/three
  MIT license; distributed as `vendor/three.LICENSE` with the site.

Dependencies are pinned in `package-lock.json`. Third-party build binaries are
copied from installed packages into the deployment artifact, not committed.
