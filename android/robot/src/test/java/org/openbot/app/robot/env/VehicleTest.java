package org.openbot.app.robot.env;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertFalse;
import static org.junit.Assert.assertTrue;

import androidx.test.core.app.ApplicationProvider;
import androidx.test.ext.junit.runners.AndroidJUnit4;
import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.openbot.app.robot.utils.Enums;
import org.openbot.app.robot.vehicle.Control;
import org.openbot.app.robot.vehicle.Vehicle;

@RunWith(AndroidJUnit4.class)
public class VehicleTest {

  private Vehicle vehicle;

  @Before
  public void setupVehicle() {
    vehicle = new Vehicle(ApplicationProvider.getApplicationContext(), 115200);
  }

  @Test
  public void getRotation() {
    assertEquals(0, vehicle.getRotation(), 0.0);

    vehicle.setControl(new Control(0.5f, 1));
    assertEquals(-60, vehicle.getRotation(), 0.0);

    vehicle.setControl(new Control(0f, 1));
    assertEquals(-180, vehicle.getRotation(), 0.0);
  }

  @Test
  public void getSpeed() {
    vehicle.setSpeedMultiplier(Enums.SpeedMode.SLOW.getValue());
    vehicle.setControl(new Control(-1, -1));

    assertEquals(-128, vehicle.getLeftSpeed(), 0.0);
    assertEquals(-128, vehicle.getRightSpeed(), 0.0);

    vehicle.setSpeedMultiplier(Enums.SpeedMode.NORMAL.getValue());
    vehicle.setControl(new Control(-1, -1));

    assertEquals(-192, vehicle.getLeftSpeed(), 0.0);
    assertEquals(-192, vehicle.getRightSpeed(), 0.0);

    vehicle.setSpeedMultiplier(Enums.SpeedMode.FAST.getValue());
    vehicle.setControl(new Control(1, 1));

    assertEquals(255, vehicle.getLeftSpeed(), 0.0);
    assertEquals(255, vehicle.getRightSpeed(), 0.0);
  }

  @Test
  public void envFeatureIsDetected() {
    assertFalse(vehicle.isHasEnvSensor());
    vehicle.processVehicleConfig("OPTIMUS:s:e:");
    assertTrue(vehicle.isHasEnvSensor());
    assertTrue(vehicle.isHasSonar());
  }

  @Test
  public void envMessageUpdatesReadings() {
    vehicle.processEnvMessage("23.4,61.2");
    assertEquals(23.4f, vehicle.getTemperature(), 0.001);
    assertEquals(61.2f, vehicle.getHumidity(), 0.001);
  }

  @Test
  public void negativeTemperatureIsAccepted() {
    vehicle.processEnvMessage("-3.5,80.0");
    assertEquals(-3.5f, vehicle.getTemperature(), 0.001);
    assertEquals(80.0f, vehicle.getHumidity(), 0.001);
  }

  @Test
  public void malformedEnvMessagesAreIgnored() {
    vehicle.processEnvMessage("23.4,61.2");
    for (String bad : new String[] {"", "1", "1,2,3", "abc,1", "1,"}) {
      vehicle.processEnvMessage(bad);
      assertEquals(23.4f, vehicle.getTemperature(), 0.001);
      assertEquals(61.2f, vehicle.getHumidity(), 0.001);
    }
  }

  @Test
  public void envReadingIsOnlyAvailableAfterValidMessage() {
    // ESP32 boot banner lines such as "ets Jun  8 2016" start with 'e'
    vehicle.processEnvMessage("ts Jun  8 2016 00:22:57");
    assertFalse(vehicle.hasEnvReading());
    vehicle.processEnvMessage("23.4,61.2");
    assertTrue(vehicle.hasEnvReading());
  }
}
