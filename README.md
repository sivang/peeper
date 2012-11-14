Peepr v0.1
==========

* A very crude simple social stream API.
* Done in time constraint of a few hours on Saturday, the weekend.
* Was a quick and dirty burn and crash - “we-need-to-have-something-running-by-today!!” development process, including learning Flask, rebrushing PostgreSQL and SQL skills as I go.
* However, I did retain proper coding and code reuse as much as time and the microframework I was using permitted. Used as much support as provided by DB API 2.0 PostgreSQL python driver (-paging a notable example).
* I decided to use Flask as it seems very light and easy to mold to crash burn development, it was also fun using it! (-as flask allows you to stay low level in Python without dealing with cruft of full blown MVCs giving great control).
* It is assumed there’s no need for user authentication and authorization.
* Error management is delegated to the RDBMS used (PostgreSQL) , and bubbled up through the Python exception mechanism. This works well since proper HTTP response codes are *always* returned accordingly - excellent if are in the “we-need-to-have-something-running-by-today” stress.
* Deployed to Heroku, using PostgreSQL hosted in Amazon EC2 through Heroku plugin (https://postgres.heroku.com/)
* REST is assumed, as in every request must encapsulate state.
* All arguments are passed through query strings.
* Responses are JSON for data.
* Named ‘Peeper’ for obvious reasons , or not?! :-D


Usage
=====

* code-block::http://peeper.herokuapp.com/get_feed/user_id
    - Get the feed for user specified by user_id , e.g. get all the peeps users users_id follows did recently.
    - optional request parameter: max_returned , to specify how many backward entries to return. defaults to 20.

* http://peeper.herokuapp.com/create_user/username
    - creates a new userid.
    - returns the newly created userid in JSON.

* http://peeper.herokuapp.com/post_message/user_id?message_text=”your message”
    * posts a new message by the user user_id, text need be passed through message_text argument and escaping for spaces and such need be taken care of before POSTing.

*  http://peeper.herokuapp.com/(un)follow/username1?followed_user=username2
    - enables or disables following of user by username1 of user by username2

* http://peeper.herokuapp.com/get_global_feed 
    - returns the global feed of all recenet pees posted, same rules apply for max_returned as in get_feed.
