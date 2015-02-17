Feature: Edit Entry
    Implement a way to edit an existing entry

    Scenario: Edit page loaded
        Given the edit page and id of 1
        When I finish loading the edit page the url is edit/1
        Then I see the text for id 1 in the text box

    Scenario: Finished editing and clicked submit
        Given the edit page of id of 1
        When I change the text to 'Edit now' and submit
        Then I see 'Edited now' in homepage
