Twitter clone
=============

>flask

Flask is a lightweight WSGI web application framework. It is designed to make getting started quick and easy, with the ability to scale up to complex applications. It began as a simple wrapper around Werkzeug and Jinja and has become one of the most popular Python web application frameworks.

This is a project intended to polish our skills.

For running the project

## Virtualenv & Dependencies
### create a virtualenv and run requirements.txt<br/>

<b> what is virtual environment ? </b><br/>
A virtual environment is a tool that helps to keep dependencies required by different projects separate by creating isolated python virtual environments for them. This is one of the most important tools that most of the Python developers use.
<br/>
<a href="https://www.geeksforgeeks.org/python-virtual-environment/" >read more... </a>

- <b>installing virtualenv</b>
<pre>$ pip install virtualenv</pre>

- <b>creating virtualenv</b>
<pre>$ virtualenv env</pre>
env is name of environment

- <b>activating virtual environment</b>
<pre>$ source env/bin/activate </pre>

- <b>run requirements.txt</b>
<pre>$ pip install -r requirements.txt</pre>

- <b>run Flask App</b>
<pre>$ python run.py</pre>
