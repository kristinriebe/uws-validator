Feature: Job list filters
  As a client
  I want to retrieve a (filtered) UWS jobs list

  Background: Set server name, headers and user account
    Given I set base URL to "uws/query"
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

  Scenario Outline: PHASE filter with invalid phase
    When I make a GET request to "?PHASE=<phase>"
    Then the response status should not be 200
    
    Examples: Invalid phases
      | phase        |
      | SUCCESS      |
      | pending      |
      | somenonsense |
      | 1345         |
 
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

  Scenario Outline: Three PHASE filters
    When I make a GET request to "?PHASE=<phase1>&PHASE=<phase2>&PHASE=<phase3>"
    Then the response status should be 200
    And all UWS elements "phase" should be one of "<phase1>, <phase2>, <phase3>"

    Examples: Phase combinations (selection)
      | phase1    | phase2    | phase3    |
      | PENDING   | QUEUED    | EXECUTING |
      | EXECUTING | COMPLETED | ARCHIVED  |
      | COMPLETED | ERROR     | ABORTED   |

  Scenario Outline: LAST filter
    When I make a GET request to "?LAST=<last>"
    Then the response status should be 200
    And the number of UWS elements "jobref" should be less than or equal to "<last>"
    
    Examples: Valid numbers for LAST
      | last |
      | 0    |
      | 3    |
      | 254  |
      | 3423 |

  Scenario Outline: LAST filter with invalid values
    When I make a GET request to "?LAST=<last>"
    Then the response status should not be 200
    # which one should it be, exactly? one of "400, 403, 404, 405"?
    
    Examples: Invalid numbers for LAST
      | last     |
      | -1       |
      | -254     |
      | sometext |

  Scenario Outline: Combination of PHASE and LAST filter
    When I make a GET request to "?PHASE=<phase>&LAST=<last>"
    Then the response status should be 200
    And the number of UWS elements "jobref" should be less than or equal to "<last>"
    
    Examples: PHASE and LAST values
      | phase      | last     |
      | COMPLETED  | 5        |
      | ERROR      | 5        |
      | ABORTED    | 5        |


  Scenario Outline: Combination of PHASE and LAST filter
    When I make a GET request to "?PHASE=<phase>&LAST=<last>"
    Then the response status should be 200
    And the number of UWS elements "jobref" should be less than or equal to "<number>"

    Examples: PHASE, LAST and expected number
    # because PENDING/QUEUED jobs have no startTime, thus should be ignored
      | phase      | last     | number |
      | PENDING    | 10       | 0      |
      | QUEUED     | 10       | 0      |


  Scenario Outline: AFTER filter
    When I make a GET request to "?AFTER=<datetime>"
    Then the response status should be 200
    # TODO: And the job startTime should be later than <datetime>
    # And the list should be sorted by startTime
    # And the list should be sorted in ascending order
    
    Examples: Valid AFTER values
      | datetime            |
      | 2015-10-26T09:15:35 |
      | 2015-10-26T09:00    |
      | 2015-10-26          |
      | 2015                |

  Scenario Outline: AFTER filter with invalid values
    When I make a GET request to "?AFTER=<datetime>"
    Then the response status should not be 200
    
    Examples: Invalid AFTER values
      | datetime               |
      | 2015-10-26T09          |
      | 2015-26-10             |
      | sometext               |
      | 2015-10-26T09:00+01:00 |
