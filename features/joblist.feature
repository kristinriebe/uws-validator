Feature: Job list filters
  As a client
  I want to retrieve a (filtered) UWS jobs list

  Background: Set server name, headers and user account
    Given I set base URL to user-defined value
    And I set "Accept" header to "application/xml"
    And I set BasicAuth username and password to user-defined values

  Scenario: Get the (complete) job list
    # Note: not sure yet how to handle it of a redirect is returned!
    When I make a GET request to base URL
    Then the response status should be 200
    And the "Content-Type" header should contain "application/xml"
    And the attribute "version" should be "1.1"
    And the UWS root element is "jobs"
    # TODO: And the UWS element "jobs" contains "jobref" elements
    # TODO: And each UWS element "jobref" contains an UWS element "id"
    # TODO: And each UWS element "jobref" contains an UWS element "href"
    # TODO: And each UWS element "jobref" contains an UWS element "phase"
    And all UWS elements "phase" should be one of "PENDING, QUEUED, EXECUTING, COMPLETED, ERROR, ABORTED, ARCHIVED, HELD, SUSPENDED, UNKNOWN"
    #valid UWS phases
    # "PENDING, QUEUED, EXECUTING, COMPLETED, ERROR, ABORTED, ARCHIVED, HELD, SUSPENDED, UNKNOWN"

  @uws1_1
  Scenario Outline: PHASE filter
    When I make a GET request to "?PHASE=<phase>"
    Then the response status should be 200
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

  @daiquiri
  Scenario Outline: PHASE filter with invalid phase
    When I make a GET request to "?PHASE=<phase>"
    Then the response status should not be 200
    
    Examples: Invalid phases
      | phase        |
      | SUCCESS      |
      | pending      |
      | somenonsense |
      | 1345         |
 
  @uws1_1
  Scenario Outline: Two PHASE filters
    When I make a GET request to "?PHASE=<phase1>&PHASE=<phase2>"
    Then the response status should be 200
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
    Then the response status should be 200
    And all UWS elements "phase" should be one of "<phase1>, <phase2>, <phase3>"

    Examples: Phase combinations (selection)
      | phase1    | phase2    | phase3    |
      | PENDING   | QUEUED    | EXECUTING |
      | EXECUTING | COMPLETED | ARCHIVED  |
      | COMPLETED | ERROR     | ABORTED   |

  @uws1_1
  Scenario Outline: LAST filter
    When I make a GET request to "?LAST=<last>"
    Then the response status should be 200
    And the number of UWS elements "jobref" should be less than or equal to "<last>"
    # TODO: And the list should be sorted by startTime
    # TODO: And the list should be sorted in ascending order

    Examples: Valid numbers for LAST
      | last |
      | 0    |
      | 3    |
      | 254  |
      | 3423 |

  @daiquiri
  Scenario Outline: LAST filter with invalid values
    When I make a GET request to "?LAST=<last>"
    Then the response status should not be 200
    # which one should it be, exactly? one of "400, 403, 404, 405"?

    Examples: Invalid numbers for LAST
      | last     |
      | -1       |
      | -254     |
      | sometext |

  @uws1_1
  Scenario Outline: Combination of PHASE and LAST filter
    When I make a GET request to "?PHASE=<phase>&LAST=<last>"
    Then the response status should be 200
    And the number of UWS elements "jobref" should be less than or equal to "<last>"

    Examples: PHASE and LAST values
      | phase      | last     |
      | COMPLETED  | 5        |
      | ERROR      | 5        |
      | ABORTED    | 5        |

  @uws1_1
  Scenario Outline: Combination of PHASE and LAST filter for jobs with no startTimes
    # jobs in QUEUED/PENDING phase have no startTime, thus should be ignored
    When I make a GET request to "?PHASE=<phase>&LAST=<last>"
    Then the response status should be 200
    And the number of UWS elements "jobref" should be equal to 0

    Examples: PHASE and LAST values for jobs with no startTime
      | phase      | last     |
      | PENDING    | 10       |
      | QUEUED     | 10       |

  @uws1_1
  Scenario Outline: AFTER filter
    When I make a GET request to "?AFTER=<datetime>"
    Then the response status should be 200
    And all UWS joblist startTimes should be later than "<datetime>"
    
    Examples: Valid AFTER values
      | datetime            |
      | 2015-10-26T09:15:35 |
      | 2015-10-26T09:00    |
      | 2015-10-26          |
      | 2015                |

  @daiquiri
  Scenario Outline: AFTER filter with invalid values
    When I make a GET request to "?AFTER=<datetime>"
    Then the response status should not be 200
    
    Examples: Invalid AFTER values
      | datetime               |
      | 2015-10-26T09          |
      | 2015-26-10             |
      | sometext               |
      | 2015-10-26T09:00+01:00 |

  @uws1_1
  Scenario Outline: Combination of PHASE and AFTER filter
    When I make a GET request to "?PHASE=<phase>&AFTER=<datetime>"
    Then the response status should be 200
    And all UWS joblist startTimes should be later than "<datetime>"

    Examples: PHASE and AFTER values
      | phase      | datetime         |
      | COMPLETED  | 2015-10-26T09:00 |
      | ERROR      | 2015-10-26T09:00 |
      | ABORTED    | 2015-10-26T09:00 |

  @uws1_1
  Scenario Outline: Combination of PHASE and AFTER filter for jobs with no startTimes
    When I make a GET request to "?PHASE=<phase>&AFTER=<datetime>"
    Then the response status should be 200
    And the number of UWS elements "jobref" should be equal to 0
    And all UWS joblist startTimes should be later than "<datetime>"

    Examples: PHASE and AFTER values for jobs with no startTime
      | phase      | datetime         |
      | PENDING    | 2015-10-26T09:00 |
      | QUEUED     | 2015-10-26T09:00 |

  @uws1_1
  Scenario Outline: Combination of LAST and AFTER filter
    When I make a GET request to "?LAST=<last>&AFTER=<datetime>"
    Then the response status should be 200
    And the number of UWS elements "jobref" should be less than or equal to "<last>"
    And all UWS joblist startTimes should be later than "<datetime>"

    Examples: PHASE and LAST values
      | datetime         | last     |
      | 2015-10-26T09:00 | 5        |
      | 2015-10-26T09:00 | 3        |
      | 2015-10-26T09:00 | 2        |


# NOTE: could also add testing for reverse order, e.g. first LAST, then PHASE-filter etc.
#       But standard does not require this explicitely, so skip it.
# NOTE: also check combinations with invalid last/date/phase values?
# NOTE: Do we really need to check invalid values? What if the server just decides to ignore them?
#       This would be totally acceptable behaviour and is not forbidden by the standard
# NOTE: the behaviour for requests with more than one LAST filter or more than
# one AFTER filter are not defined, so won't be tested.
