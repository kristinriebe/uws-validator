# This feature tests
# 1) if a job list is returned properly
# 2) if the new UWS1.1 phase filters are applied correctly
# The testing involves now also the creation of new jobs for proper testing
# of job list filtering.

Feature: Job list filters
  In order to retrieve a subset of UWS jobs from a UWS service
  As a client
  I apply different filters to the UWS job list

  Background: Set server name, headers and user account
    Given I set base URL to user-defined value
      And I set BasicAuth username and password to user-defined values

  @basics
  Scenario: Get the job list
    # Note: not sure yet how to handle it if a redirect is returned!
    When I make a GET request to base URL
    Then the response status should be "200"
     And the "Content-Type" header should contain "xml"
     And the UWS root element should be "jobs"

  Scenario: Check structure of existing job list
    # Use this scenario especially if no job creation possible
    # NOTE: this will fail if there are no jobs available at all!
    When I make a GET request to base URL
    Then the response status should be "200"
     And the UWS root element should be "jobs"
     # Actually works only if the job list is not empty:
     And the UWS root element should contain UWS elements "jobref"
     And each UWS element "jobref" should have an attribute "id"
    # TODO: And each UWS element "jobref"  should have an attribute  "xlink:href"
    # --> the links are actually optional in the UWS schema!!!
     And each UWS element "jobref" should have an element "phase"
     And all UWS elements "phase" should be one of "PENDING, QUEUED, EXECUTING, COMPLETED, ERROR, ABORTED, HELD, SUSPENDED, UNKNOWN"
     # and phase should never be ARCHIVED, unless explicitely asked for!

  Scenario: Create jobs and then get the job list
    # This is more useful than the previous scenario, but needs to create jobs,
    # thus takes longer
    When I create a user-defined "veryshort" job
     And I create a user-defined "veryshort" job
     And I send PHASE="RUN" to the phase of the same job
     And I create a user-defined "veryshort" job
     And I send PHASE="ABORT" to the phase of the same job
     And I create a user-defined "error" job
     And I send PHASE="RUN" to the phase of the same job
     And I make a GET request to base URL
    Then the response status should be "200"
     And the UWS root element should be "jobs"
     And the UWS root element should contain UWS elements "jobref"
    # TODO: And each UWS element "jobref"  should have an attribute  "id"
    # TODO: And each UWS element "jobref"  should have an attribute  "xlink:href" # this is optional
    # TODO: And each UWS element "jobref"  should have an element "phase"
     And all UWS elements "phase" should be one of "PENDING, QUEUED, EXECUTING, COMPLETED, ERROR, ABORTED, HELD, SUSPENDED, UNKNOWN"
     # and phase should never be ARCHIVED, unless explicitely asked for!

  @uws1_1
  @version
  Scenario: Get the (complete) job list for UWS 1.1
    When I make a GET request to base URL
    Then the attribute "version" should be "1.1"

  @uws1_1
  Scenario Outline: PHASE filter
    When I make a GET request to "?PHASE=<phase>"
    Then the response status should be "200"
     And all UWS elements "phase" should be "<phase>"

    Examples: Valid phases
      | phase     |
      | PENDING   |
      | QUEUED    |
      | EXECUTING |
      | COMPLETED |
      | ERROR     |
      | ABORTED   |
      | ARCHIVED  |
      | HELD      |
      | SUSPENDED |
      | UNKNOWN   |

  @invalid
  @uws1_1
  Scenario Outline: PHASE filter with invalid phase
    When I make a GET request to "?PHASE=<phase>"
    Then the response status should not be "200"
    
    Examples: Invalid phases
      | phase        |
      | SUCCESS      |
      | pendinggg    |
      | somenonsense |
      | 1345         |
 
  @uws1_1
  Scenario Outline: Two PHASE filters
    When I make a GET request to "?PHASE=<phase1>&PHASE=<phase2>"
    Then the response status should be "200"
     And all UWS elements "phase" should be one of "<phase1>, <phase2>"

    Examples: Phase combinations (selection)
      | phase1    | phase2    |
      | PENDING   | ERROR    |
      | COMPLETED | ERROR     |
      | ERROR     | ABORTED   |
    # NOTE: better avoid testing with EXECUTING and QUEUED phase since they
    # may change right in between while testing!

  @uws1_1
  Scenario Outline: Three PHASE filters
    When I make a GET request to "?PHASE=<phase1>&PHASE=<phase2>&PHASE=<phase3>"
    Then the response status should be "200"
     And all UWS elements "phase" should be one of "<phase1>, <phase2>, <phase3>"

    Examples: Phase combinations (selection)
      | phase1    | phase2    | phase3    |
      | PENDING   | QUEUED    | EXECUTING |
      | EXECUTING | COMPLETED | ARCHIVED  |
      | COMPLETED | ERROR     | ABORTED   |

  @slow
  @uws1_1
  Scenario Outline: LAST filter
    When I make a GET request to "?LAST=<last>"
    Then the response status should be "200"
     And the number of UWS elements "jobref" should be less than or equal to "<last>"
     And the UWS joblist should be sorted by creationTime in descending order

    Examples: Valid numbers for LAST
      | last |
      | 1    |
      | 3    |
      | 120  |
      | 254  |
      | 3423 |

  @invalid
  @uws1_1
  Scenario Outline: LAST filter with invalid values
    When I make a GET request to "?LAST=<last>"
    Then the response status should not be "200"
    # which one should it be, exactly? one of "400, 403, 404, 405"?

    Examples: Invalid numbers for LAST
      | last     |
      | -1       |
      | -254     |
      | sometext |

  @slow
  @uws1_1
  Scenario Outline: Combination of PHASE and LAST filter
    When I make a GET request to "?PHASE=<phase>&LAST=<last>"
    Then the response status should be "200"
     And the number of UWS elements "jobref" should be less than or equal to "<last>"
     And the UWS joblist should be sorted by creationTime in descending order

    Examples: PHASE and LAST values
      | phase      | last     |
      | COMPLETED  | 5        |
      | ERROR      | 5        |
      | ABORTED    | 5        |


  @slow
  @uws1_1
  Scenario Outline: AFTER filter with different valid date formats
    When I make a GET request to "?AFTER=<datetime>"
    Then the response status should be "200"
     And all UWS joblist creationTimes should be later than "<datetime>"
    
    Examples: Valid AFTER values
      | datetime            |
      | 2015-10-26T09:15:35 |
      | 2015-10-26 09:00    |
      | 2015-10-26          |
      | 2015                |
      | 20151026            |
#      | 2015-W01            |


  @invalid
  @uws1_1
  Scenario Outline: AFTER filter with invalid values
    When I make a GET request to "?AFTER=<datetime>"
    Then the response status should not be "200"

    Examples: Invalid AFTER values
      | datetime               |
#      | 2015-10-26T09          |
      | 2015-26-10             |
      | sometext               |
      | 2015-10-26T09:00+01:00 |

  @test
  @slow
  @uws1_1
  Scenario: AFTER filter using creationTime from job list
    When I make a GET request to base URL
     And I pick a creationTime from the job list
     And I apply the AFTER filter with the stored creationTime
    Then the response status should be "200"
     And the number of UWS elements "jobref" should be greater than or equal to "1"
#     And the number of UWS elements "jobref" should be less than the total number of jobs
     And all UWS joblist creationTimes should be later than the stored creationTime

  @slow
  @uws1_1
  Scenario Outline: Combination of PHASE and AFTER filter
    When I make a GET request to "?PHASE=<phase>&AFTER=<datetime>"
    Then the response status should be "200"
     And all UWS joblist creationTimes should be later than "<datetime>"

    Examples: PHASE and AFTER values
      | phase      | datetime         |
      | COMPLETED  | 2015-10-26T09:00 |
      | ERROR      | 2015-10-26T09:00 |
      | ABORTED    | 2015-10-26T09:00 |

  @slow
  @uws1_1
  Scenario Outline: Combination of LAST and AFTER filter
    When I make a GET request to "?LAST=<last>&AFTER=<datetime>"
    Then the response status should be "200"
     And the number of UWS elements "jobref" should be less than or equal to "<last>"
     And all UWS joblist creationTimes should be later than "<datetime>"
     And the UWS joblist should be sorted by creationTime in descending order

    Examples: AFTER and LAST values
      | datetime         | last     |
      | 2015-10-26T09:00 | 5        |
      | 2015-10-26T09:00 | 3        |
      | 2015-10-26T09:00 | 2        |

# NOTE: could also add testing for reverse order, e.g. first LAST, then PHASE-filter etc.
#       But standard does not require this explicitely, so skip it.
# NOTE: Check invalid values? What if the server just decides to ignore them?
#       This would be totally acceptable behaviour and is not forbidden by the standard
# NOTE: The behaviour for requests with more than one LAST filter or more than
#       one AFTER filter are not defined by the standard, so won't be tested.
