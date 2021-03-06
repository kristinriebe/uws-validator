Feature: User Account
  As a client
  I want to access the uws-endpoint

  Background: Set server name, headers and user account
    Given I set base URL to user-defined value
    And I set BasicAuth username and password to user-defined values

  @basics
  Scenario: Ensure user can access UWS endpoint
    When I make a GET request to base URL
    Then the response status should be "200"
