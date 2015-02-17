Feature: MarkDown
    Implement a way to MarkDown an entry to be able to make pretty

    Scenario: Entry text contains MarkDown language
        Given Entry has text with "# Header"
        When I go to the detail page of id 2
        Then I see a H1 tag