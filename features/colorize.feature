Feature: Colorize
    Implement a way to colorize text

    Scenario: Code tag is submitted via text box
        Given an entry with colorized code
        When I go to the detail page with id3
        Then I will see the tag for codehilite