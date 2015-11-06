# This feature tests
# 1) if a job list is returned properly
# 2) if the new UWS1.1 phase filters are applied correctly
# The testing is done passively, i.e. no new jobs are created,
# just the ones that can be retrieved can be filtered.
# This is not as elaborate as it could be, but is a good starting point for
# testing if the user cannot create new jobs.

Feature: Job list filters
  As a client
  I want to retrieve a (filtered) list of UWS jobs

  Background: Set server name, headers and user account
    Given I set base URL to user-defined value
    And I set "Accept" header to "application/xml"
    And I set BasicAuth username and password to user-defined values

  @basics
  Scenario: Get the (complete) job list (possibly with 0 elements!)
    # Note: not sure yet how to handle it if a redirect is returned!
    When I make a GET request to base URL
    Then the response status should be "200"
    And the "Content-Type" header should contain "application/xml"
    And the UWS root element should be "jobs"

  Scenario: Get the (complete) job list
    # Note: not sure yet how to handle it if a redirect is returned!
    When I make a GET request to base URL
    Then the response status should be "200"
    And the "Content-Type" header should contain "application/xml"
    And the UWS root element should be "jobs"

  Scenario: Create jobs and get the job list
    When I create a user-defined immediate job
    And I create and start a user-defined immediate job
    And I make a GET request to base URL
    Then the response status should be "200"
    And the UWS root element should be "jobs"
    And the UWS root element should contain UWS elements "jobref"
    # TODO: And each UWS element "jobref" should contain an UWS element "id"
    # TODO: And each UWS element "jobref" should contain an UWS element "href"
    # TODO: And each UWS element "jobref" should contain an UWS element "phase"
    And all UWS elements "phase" should be one of "PENDING, QUEUED, EXECUTING, COMPLETED, ERROR, ABORTED, ARCHIVED, HELD, SUSPENDED, UNKNOWN"

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
  Scenario Outline: PHASE filter with invalid phase
    When I make a GET request to "?PHASE=<phase>"
    Then the response status should not be "200"
    
    Examples: Invalid phases
      | phase        |
      | SUCCESS      |
      | pending      |
      | somenonsense |
      | 1345         |
 
  @uws1_1
  Scenario Outline: Two PHASE filters
    When I make a GET request to "?PHASE=<phase1>&PHASE=<phase2>"
    Then the response status should be "200"
    And all UWS elements "phase" should be one of "<phase1>, <phase2>"

    Examples: Phase combinations (selection)
      | phase1    | phase2    |
      | PENDING   | QUEUED    |
      | EXECUTING | COMPLETED |
      | COMPLETED | ERROR     |
      | ERROR     | ABORTED   |

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
    And the UWS joblist should be sorted by startTime in ascending order

    Examples: Valid numbers for LAST
      | last |
      | 0    |
      | 3    |
      | 254  |
      | 3423 |

  @invalid
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
    And the UWS joblist should be sorted by startTime in ascending order

    Examples: PHASE and LAST values
      | phase      | last     |
      | COMPLETED  | 5        |
      | ERROR      | 5        |
      | ABORTED    | 5        |

  @slow
  @uws1_1
  Scenario Outline: Combination of PHASE and LAST filter for jobs with no startTimes
    # jobs in QUEUED/PENDING phase have no startTime, thus should be ignored
    When I make a GET request to "?PHASE=<phase>&LAST=<last>"
    Then the response status should be "200"
    And the number of UWS elements "jobref" should be equal to 0
    And the UWS joblist should be sorted by startTime in ascending order

    Examples: PHASE and LAST values for jobs with no startTime
      | phase      | last     |
      | PENDING    | 10       |
      | QUEUED     | 10       |

  @slow
  @uws1_1
  Scenario Outline: AFTER filter
    When I make a GET request to "?AFTER=<datetime>"
    Then the response status should be "200"
    And all UWS joblist startTimes should be later than "<datetime>"
    
    Examples: Valid AFTER values
      | datetime            |
      | 2015-10-26T09:15:35 |
      | 2015-10-26T09:00    |
      | 2015-10-26          |
      | 2015                |

  @invalid
  Scenario Outline: AFTER filter with invalid values
    When I make a GET request to "?AFTER=<datetime>"
    Then the response status should not be "200"

    Examples: Invalid AFTER values
      | datetime               |
      | 2015-10-26T09          |
      | 2015-26-10             |
      | sometext               |
      | 2015-10-26T09:00+01:00 |

  @slow
  @uws1_1
  Scenario Outline: Combination of PHASE and AFTER filter
    When I make a GET request to "?PHASE=<phase>&AFTER=<datetime>"
    Then the response status should be "200"
    And all UWS joblist startTimes should be later than "<datetime>"

    Examples: PHASE and AFTER values
      | phase      | datetime         |
      | COMPLETED  | 2015-10-26T09:00 |
      | ERROR      | 2015-10-26T09:00 |
      | ABORTED    | 2015-10-26T09:00 |

  @slow
  @uws1_1
  Scenario Outline: Combination of PHASE and AFTER filter for jobs with no startTimes
    When I make a GET request to "?PHASE=<phase>&AFTER=<datetime>"
    Then the response status should be "200"
    And the number of UWS elements "jobref" should be equal to 0
    And all UWS joblist startTimes should be later than "<datetime>"

    Examples: PHASE and AFTER values for jobs with no startTime
      | phase      | datetime         |
      | PENDING    | 2015-10-26T09:00 |
      | QUEUED     | 2015-10-26T09:00 |

  @slow
  @uws1_1
  Scenario Outline: Combination of LAST and AFTER filter
    When I make a GET request to "?LAST=<last>&AFTER=<datetime>"
    Then the response status should be "200"
    And the number of UWS elements "jobref" should be less than or equal to "<last>"
    And all UWS joblist startTimes should be later than "<datetime>"
    And the UWS joblist should be sorted by startTime in ascending order

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
