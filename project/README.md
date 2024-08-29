# MATHCARDS
#### Video Demo: https://youtu.be/hAeFAhEQYQY
#### Description:


#### Register, Login and Logout
Register, login and logout all have the same implementation as in finance, with css to change the ui.


#### Mathcards database
The mathcards database has 4 tables. Table 1 is users (same as finance). Table 2 is decks which stores the name of the deck, the user it belongs to and its unique id. Table 3 is cards which stores the card id, text at the front and text at the back. It uses foreign keys from decks and users to know which deck and which user it belongs to. The final table is math_symbols which stores the name of the symbol and its code in mathJax.


#### Homepage
Here all of the decks you have created are displayed, and you have the ability to delete and add new decks.

The **delete_decks** function works and has similar implementation to the **delete** function in the problems set birthdays.

When a delete button is clicked, the user gets redirected from the **homepage** function to the **delete_deck** function, which stores the id of said deck, and then to the **check** function. This then displays a prompt **(check.html)** to see if the user is sure they want to delete the deck.

When adding a deck, the **homepage** function checks first if the name of the deck that the user has inputted isn’t null and is unique to prevent confusion. It then inserts this into the mathcards database.


**There are 3 tabs in the navigation bar: add cards, edit cards and revision.**

#### Add cards
When add cards is clicked we get redirected to the **adding_cards** function which displays **add.html**. The user is able to select the deck that it wants to add the card to and fill in the front and back of the flashcard. This is then inserted into a different table in the mathcards database. When a user inputs something into the mathematics box, we get redirected to the **maths** function, which allows us to dynamically search through a database of mathematical symbols to find which symbols the user wants to add to the flashcard. This function then returns the symbol as a button in mathjax code, which is then rendered by the javascript in **add.html**. If one of those buttons are clicked we get redirected to the **symbol_clicked** function, which returns the mathjax code of the symbol into either the front or back input of the flashcard. Finally, there are two buttons, front and back, which the user can click to decide where they want the code for the symbol appended to.

#### Edit cards
When edit cards is clicked, we get redirected to **search** so that we can find the flashcard that the user wants to edit. Here the user has three options. The third option is to filter the cards by deck through a dropdown menu. The second option is to just find the card you are looking for out of every card manually through a dropdown menu. The first option is to dynamically search for the card by entering something similar to the text at the front of the card. This uses the **searching function** and **searching.html** to update the list of cards in the dropdown menu in option 2. Once the card is selected, we are redirected to the **edit** function which is essentially the same as the **add** function, except there is a delete button which uses the **delete_card** function to delete the card from the database.


#### Revision
When revision is clicked the user is redirected to the **revision_decks** function. This displays a list of the users decks and the ability to select multiple decks before submitting the decks they want to revise using **revision.html**. Once submitted, the cards in those decks are shuffled and the user is redirected to the **revision** function. This function then permutes through the cycle of cards, displaying the front of the card and then the back of the card once the user is ready using **revision.html**.

For design, I would have liked this to be similar to anki, where the user is given 4 options and can tell the server how hard it found the flashcard, which then uses an algorithm to determine when that card should next be revised. However, this seemed relatively complex (deciding how long until the user should revise the card) and would require a lot of work. Since this wasn’t the main focus of the project, I decided against implementing it.
