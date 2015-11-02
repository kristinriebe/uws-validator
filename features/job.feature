Feature: Job
  As a UWS client
  I want to create and access a job

  Background: Set server name, headers and user account
    Given I set base URL to user-defined value
    And I set BasicAuth username and password to user-defined values

#  Scenario: Test POST request
#    When I make a POST request to "/"
#    """
#    {"query": "SELECT * FROM MDR1.FOF LIMIT 10"}
#    """
#    Then the response status should be 200
#    And the response body should contain
#    """
#    <?xml version=\"1.0\" ?>
#    <uws:job version=\"1.1\" xmlns:uws=\"http://www.ivoa.net/xml/UWS/v1.0\" xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\">
#        <uws:jobId>1445945379095063623</uws:jobId>
#        <uws:ownerId>uwstest</uws:ownerId>
#        <uws:phase>PENDING</uws:phase>
#        <uws:quote xsi:nil=\"true\"/>
#        <uws:startTime xsi:nil=\"true\"/>
#        <uws:endTime xsi:nil=\"true\"/>
#        <uws:executionDuration>0</uws:executionDuration>
#        <uws:destruction xsi:nil=\"true\"/>
#        <uws:parameters>
#            <uws:parameter id=\"query\">SELECT * FROM MDR1.FOF LIMIT 10</uws:parameter>
#        </uws:parameters>
#        <uws:results/>
#    </uws:job>
#    """

  Scenario: Check a pending job
    Given I set "Accept" header to "application/xml"
    When I make a GET request to "1445429492409191723"
    Then the response status should be 200
    And the "Content-Type" header should contain "application/xml"
    And the attribute "version" should be "1.1"
    And the UWS element "ownerId" should be "tuser"
    And the UWS element "phase" should be "PENDING"
    And the UWS element "phase" should exist
    And the UWS element "phase" should be one of "PENDING, QUEUED, EXECUTING, COMPLETED, ERROR, ABORTED, ARCHIVED, HELD, SUSPENDED, UNKNOWN"
    # And the parameter "startTime" should be "Null"

  Scenario: Ensure correct phase
    When I make a GET request to "1445429492409191723/phase"
    Then the response status should be 200
    And the response body should contain "PENDING"

#  Scenario: Create and check pending job
#    When I create a new job with
#    #When I make a POST request to "/" with
#        | qkey   | qvalue      |
#        | query  | SELECT * FROM MDR1.FOF LIMIT 10 |
#    
#    And GET the job afterwards
#    #And I make a GET request to "{jobId}/phase".format(jobId=context.job.get_jobId()))
#    Then the response status should be 200
#    And the response body should contain "PENDING"
#    #And the element "phase" should be "PENDING"
#    # Now I should remove the job!!

# TODO: continue with WAIT parameter for PENDING job