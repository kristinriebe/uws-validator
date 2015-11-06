Feature: Job
  In order to be notified when a job changes
  As a UWS client
  I want to WAIT for phase changes or if a specified time has passed or the server times out

  Background: Set server name, headers and user account
    Given I set base URL to user-defined value
    And I set BasicAuth username and password to user-defined values

  @uws1_1
  Scenario: (Do not) Wait for job in inactive phase
    When I create and start a user-defined immediate job
    And I send PHASE="ABORT" to the phase of the same job
    And I use blocking with WAIT="100"
    Then the server should return immediately

  @slow
  @uws1_1
  Scenario: Wait for job in active phase
    When I create a user-defined immediate job
    And I use blocking with WAIT="5"
    Then the request time should be at least the wait time
    And the request time should not be much longer than the wait time

  @uws1_1
  Scenario Outline: (Do not) Wait for job with specified inactive phase
    When I create a user-defined immediate job
    And I use advanced blocking with WAIT="5" and PHASE="<phase>"
    Then the server should return immediately

    Examples: Inactive phases
      | phase     |
      | COMPLETED |
      | ERROR     |
      | ABORTED   |
      | ARCHIVED  |
      | HELD      |
      | SUSPENDED |
      | UNKNOWN   |

  @slow
  @uws1_1
  Scenario Outline: Wait for job with specified active phase
    When I create a user-defined immediate job
    And I use advanced blocking with WAIT="5" and PHASE="<phase>"
    Then the request time should be at least the wait time
    And the request time should not be much longer than the wait time

    Examples: Active phases
      | phase     |
      | PENDING   |


  @uws1_1
  Scenario Outline: (Do not) Wait for job with phase mismatch
    When I create a user-defined immediate job
    And I use advanced blocking with WAIT="5" and PHASE="<phase>"
    Then the server should return immediately

    Examples: Active phases, mismatching
      | phase       |
      | EXECUTING   |
      | QUEUED      |

  @phasechange
  @slow
  @uws1_1
  # This only works if there is some kind of job queue and if the job
  # runs less than 20 seconds, but more than ~ 2 seconds.
  Scenario: Wait for job phase change
    When I create a user-defined short job
    And I send PHASE="RUN" to the phase of the same job
    And I use advanced blocking with WAIT="20" and PHASE="QUEUED"
    And I use advanced blocking with WAIT="20" and PHASE="EXECUTING"
    Then the server should not return immediately
    And the request time should be shorter than the wait time
    And the UWS element "phase" should be "COMPLETED" 

  @veryslow
  @uws1_1
  Scenario: Wait forever
    When I create a user-defined short job
    And I use advanced blocking with WAIT="-1"
    Then the server should not return immediately
    # since we never start this job, the wait is only limited by the server timeout


# NOTE: Cannot test behaviour with queued/executing jobs, since I cannot control
#       how long a job waits in queue or how long it runs

# NOTE: Which behavious is expected, if the multiple phases are provided with WAIT?
#       I would say it's not allowed, so return with error?
