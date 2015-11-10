Feature: Job
  In order to deal with UWS jobs
  As a UWS client
  I want to create a job, start it, abort it, update it and check its details

  Background: Set server name, headers and user account
    Given I set base URL to user-defined value
      And I set BasicAuth username and password to user-defined values

  @basic
  Scenario: Create pending job
    When I create a user-defined "veryshort" job
    Then the response status should be "200"
     And the UWS root element should be "job"
     And the UWS element "jobId" should exist
     And the UWS element "ownerId" should exist
     And the UWS element "executionDuration" should exist
     And the UWS element "phase" should be "PENDING"

  @version
  @uws1_1
  Scenario: Create pending job for UWS 1.1 service, check version attribute
    When I create a user-defined "veryshort" job
    Then the attribute "version" should be "1.1"

  Scenario: Create job and remove
    When I create a user-defined "veryshort" job
     And I delete the same job
    Then the response status should be "200"
     And the UWS root element should be "jobs"

    When I get the job details of the same job
    Then the response should be status "404" or the job has phase "ARCHIVED"

  Scenario: Create job and abort
    When I create a user-defined "veryshort" job
     And I send PHASE="ABORT" to the phase of the same job
    Then the response status should be "200"
     And the UWS element "phase" should be "ABORTED"
     And the UWS element "endTime" should exist

  Scenario: Create job and start
    When I create a user-defined "veryshort" job
     And I send PHASE="RUN" to the phase of the same job
    Then the response status should be "200"
     And the UWS element "phase" should be one of "QUEUED, EXECUTING, COMPLETED"
    # should not be error/aborted or so, ARCHIVED could happen as well, if job is destructed  immediately; ABORTED could happen on timeout, but we asked the user to provide a**veryshort** running job,
    # could also be something like "SELECT 100" if the server allows this.
    # We could also include a sleep() for a few seconds before checking job status, but this would slow down the whole testing process.

  @optional
  Scenario: [Optional] Create and start job in one step
    When I create and start a user-defined "veryshort" job
    Then the response status should be "200"
     And the UWS element "phase" should be one of "QUEUED, EXECUTING, COMPLETED"

  # TODO: Scenario: Create a pending job, update parameters
  #                 But this would be very service-specific!

  #@need_wait
  @slow
  Scenario: Create a job with error
    When I create a user-defined "error" job
     And I send PHASE="RUN" to the phase of the same job
    #And I use advanced blocking with WAIT="-1" and PHASE="QUEUED"
    #And I use advanced blocking with WAIT="-1" and PHASE="EXECUTING"
    # or, if no WAIT-parameter supported:
     And I check the same job every "2" seconds until it is in a final state
    Then the UWS element "phase" should be "ERROR"
     And the UWS element "startTime" should exist
     And the UWS element "endTime" should exist

  #@need_wait
  @slow
  @queue
  # The following scenario will only work if the server does not block and wait until the job is done!
  # I.e. it's asynchronous, there must be a queueing system behind it
  Scenario: Create a long job and abort
    When I create a user-defined "long" job
     And I send PHASE="RUN" to the phase of the same job
     # And I use advanced blocking with WAIT="-1" and PHASE="QUEUED"
     And I check the same job every "2" seconds until it starts or is aborted/deleted
     And I send PHASE="ABORT" to the phase of the same job
     And I wait for "1" seconds
    Then the UWS element "phase" should be "ABORTED"
     And the UWS element "endTime" should exist

# TODO: how can I properly check later on, after some time has passed, if a long job ever reached the COMPLETED phase?
