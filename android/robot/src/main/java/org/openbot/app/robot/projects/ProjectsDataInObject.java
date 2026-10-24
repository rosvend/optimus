package org.openbot.app.robot.projects;

public class ProjectsDataInObject {
  private final String projectId;
  private final String projectName;
  private final long dateMs;
  private final String projectCommands;

  public ProjectsDataInObject(
      String projectId, String projectName, long dateMs, String projectCommands) {
    this.projectId = projectId;
    this.projectName = projectName;
    this.dateMs = dateMs;
    this.projectCommands = projectCommands;
  }

  public String getProjectId() {
    return projectId;
  }

  public String getProjectName() {
    return projectName;
  }

  public long getProjectDate() {
    return dateMs;
  }

  public String getProjectCommands() {
    return projectCommands;
  }
}