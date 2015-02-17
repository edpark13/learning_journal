Feature: Permalink
    Implement a way to go to detailed page of an entry with a link

    Scenario: Navigates to correct permalink and correct text displays
        Given entry with id 1
        When I go to the url 
        Then I see that it is detail/1 and the text for id 1 displays
