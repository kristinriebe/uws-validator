Feature: Job list filters
  As a client
  I want to retrieve a (filtered) UWS jobs list

  Background: Set server name, headers and user account
    Given I set base URL to "uws/query"
    And I set BasicAuth username and password to user-defined values

  Scenario: Get the (complete) job list
    # Note: not sure yet how to handle it of a redirect is returned!
    Given I set "Accept" header to "application/xml"
    When I make a GET request to base URL
    Then the response status should be 200
    And the "Content-Type" header should contain "application/xml"
    And the attribute "version" should be "1.1"
    And the UWS root element is "jobs"
    # And the UWS element "jobs" contains "jobref" elements
    # And each UWS element "jobref" contains an UWS element "id"
    # And each UWS element "jobref" contains an UWS element "href"
    # And each UWS element "jobref" contains an UWS element "phase"
    And all UWS elements "phase" should be one of "PENDING, QUEUED, EXECUTING, COMPLETED, ERROR, ABORTED, ARCHIVED, HELD, SUSPENDED, UNKNOWN"
    #valid UWS phases
    # "PENDING, QUEUED, EXECUTING, COMPLETED, ERROR, ABORTED, ARCHIVED, HELD, SUSPENDED, UNKNOWN"

  Scenario Outline: PHASE filters
    Given I set "Accept" header to "application/xml"
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

  Scenario Outline: LAST filter
    Given I set "Accept" header to "application/xml"
    When I make a GET request to "?LAST=<last>"
    Then the response status should be 200
    And the number of UWS elements "jobref" should be less than or equal to "<last>"
    
    Examples: Valid numbers for last
      | last |
      | 0    |
      | 3    |
      | 254  |
      | 3423 |

  Scenario Outline: LAST filter with invalid values
    Given I set "Accept" header to "application/xml"
    When I make a GET request to "?LAST=<last>"
    Then the response status should not be 200
    # which one should it be, exactly?? one of "400, 403, 404, 405"?
    
    Examples: Invalid numbers for last
      | last     |
      | -1       |
      | -254     |
      | sometext |


