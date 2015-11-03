Feature: Job
  As a UWS client
  I want to create and access a job

  Background: Set server name, headers and user account
    Given I set base URL to user-defined value
    And I set BasicAuth username and password to user-defined values

  Scenario: Create and remove pending job
    When I create a user-defined short job
    Then the response status should be "200"
    And the attribute "version" should be "1.1"
    # And the "Content-Type" header should contain "application/xml"
    And the UWS element "phase" should be "PENDING"

    When I delete the same job
    Then the response status should be "200"
    #TODO: And the job list should be returned

    When I get the job details of the same job
    Then the response should either be status "404" or the job has phase "ARCHIVED"

  @test
  Scenario: Create and abort pending job
    When I create a user-defined short job
    And I send PHASE="ABORT" to the phase of the same job
    Then the response status should be "200"

    When I get the job details of the same job
    Then the response status should be "200"
    And the UWS element "phase" should be "ABORTED"
    And the UWS element "endTime" should exist

    # delete job afterwards --> should store jobIds somewhere and then clean up later on, if after_all
    When I delete the same job
    Then the response status should be "200"

  Scenario: Create and start pending job


  Scenario: Create and start pending job in one step

# TODO: continue with WAIT parameter for PENDING job