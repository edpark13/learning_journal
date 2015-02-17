Feature: Homepage
    Implement a way to see the homepage

    Scenario: Home page loaded
        Given the homepage
        When I navigate to index.html
        Then I see the homepage