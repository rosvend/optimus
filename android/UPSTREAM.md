# Origen

Copia de `android/` de [ob-f/OpenBot](https://github.com/ob-f/OpenBot) en el commit `0aac230` (2026-10-06), con licencia MIT (ver `LICENSE`).

## Cambios propios de Optimus

- `robot/src/main/java/org/openbot/app/robot/vehicle/Vehicle.java`: sensor ambiental (`:e:` en features, mensaje `e<°C>,<%HR>`).
- `robot/src/main/java/org/openbot/app/robot/common/ControlsFragment.java`: despacha el mensaje `e`.
- `robot/src/main/java/org/openbot/app/robot/robot/RobotInfoFragment.java`: muestra temperatura y humedad.
- `robot/src/main/res/layout/fragment_robot_info.xml`, `robot/src/main/res/values/strings.xml`: fila "Temp / Humedad".
- `robot/src/test/java/org/openbot/app/robot/env/VehicleTest.java`: tests del mensaje `e`.

## Compilar

Abrir esta carpeta (`android/`) en Android Studio, o ejecutar `./gradlew :robot:assembleDebug`. Desinstalar el OpenBot de la Play Store antes de instalar (mismo `applicationId`).
