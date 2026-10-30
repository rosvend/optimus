# Origen

Copia de `android/` de [ob-f/OpenBot](https://github.com/ob-f/OpenBot) en el commit `0aac230` (2026-10-06), con licencia MIT (ver `LICENSE`).

## Cambios propios de Optimus

- `robot/src/main/java/org/openbot/app/robot/vehicle/Vehicle.java`: sensor ambiental (`:e:` en features, mensaje `e<°C>,<%HR>`).
- `robot/src/main/java/org/openbot/app/robot/common/ControlsFragment.java`: despacha el mensaje `e`. Al conceder los permisos del controlador en modo Web abre la señalización (`connectWebServer`) en vez de Nearby, y una denegación previa ya no bloquea las siguientes.
- `robot/src/main/java/org/openbot/app/robot/robot/FreeRoamFragment.java`, `logging/LoggerFragment.java`: en modo Web, `DISCONNECTED` (un navegador que se va, o el dashboard reiniciando el vídeo) ya no pasa a Gamepad ni cierra el WebSocket de señalización.
- Cámara compartida entre el detector y el streaming WebRTC (Android solo deja un cliente por cámara, y el `Camera2Capturer` de WebRTC se la quitaba al seguimiento de personas):
  - `robot/src/main/java/org/openbot/app/robot/env/SharedCameraCapturer.java` (nuevo): `VideoCapturer` que recibe los frames de la pantalla que tiene la cámara abierta.
  - `robot/src/main/java/org/openbot/app/robot/common/CameraFragment.java`: marca la cámara como suya entre `onStart` y `onStop`, y manda cada frame (derecho, a 640 px y 15 fps como máximo) con el dibujo de `drawStreamOverlay` al stream.
  - `robot/src/main/java/org/openbot/app/robot/env/WebRtcServer.java`: usa `SharedCameraCapturer` cuando una pantalla tiene la cámara, y reinicia el stream cuando eso cambia.
  - `robot/src/main/java/org/openbot/app/robot/objectNav/ObjectNavFragment.java`, `robot/src/main/java/org/openbot/app/robot/tracking/MultiBoxTracker.java`: dibujan las cajas de las personas detectadas sobre el stream.
- `robot/src/main/java/org/openbot/app/robot/robot/RobotInfoFragment.java`: muestra temperatura y humedad.
- `robot/src/main/res/layout/fragment_robot_info.xml`, `robot/src/main/res/values/strings.xml`: fila "Temp / Humedad".
- `robot/src/test/java/org/openbot/app/robot/env/VehicleTest.java`: tests del mensaje `e`.
- `robot/src/main/java/org/openbot/app/robot/telemetry/`, `robot/telemetry.properties.example`: subida de telemetría al microservicio FIWARE (`fiware/`), antes a AWS.

## Compilar

Abrir esta carpeta (`android/`) en Android Studio, o ejecutar `./gradlew :robot:assembleDebug`. Desinstalar el OpenBot de la Play Store antes de instalar (mismo `applicationId`).
