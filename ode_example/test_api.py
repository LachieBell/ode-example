#!/usr/bin/env python
import requests
import turtle


def simulate_ode(transmission_rate=4,
                 recovery_rate=1,
                 initial_percent_infected=0.1,
                 max_t=50):
    """Simple as requests call to demonstrate api"""

    url = 'http://localhost:8000/solve_ode/'
    data = {'transmission_rate': transmission_rate,
            'recovery_rate': recovery_rate,
            'initial_percent_infected': initial_percent_infected,
            'max_t': max_t}

    return requests.get(url, params=data).json()


OFFSET_TURTLE_X = -400
OFFSET_TURTLE_Y = -100
SCALE_TURTLE_X = 20
SCALE_TURTLE_Y = 300


def turtle_print_results(results):
    """I would do this in like matplotlib or something, but I want to keep
    requirements.txt to a minimum. Turtle graphics are part of the standard
    package though. So that's cool right?"""

    recovery = results['recovered']
    infected = results['infected']
    susceptible = results['susceptible']

    recovery_turtle = turtle.Turtle()
    recovery_turtle.pencolor('red')
    recovery_turtle.speed(1)
    recovery_turtle.penup()
    recovery_turtle.goto(OFFSET_TURTLE_X, OFFSET_TURTLE_Y + recovery[0]*SCALE_TURTLE_Y)
    recovery_turtle.pendown()

    infected_turtle = turtle.Turtle()
    infected_turtle.pencolor('green')
    infected_turtle.speed(1)
    infected_turtle.penup()
    infected_turtle.goto(OFFSET_TURTLE_X, OFFSET_TURTLE_Y + infected[0]*SCALE_TURTLE_Y)
    infected_turtle.pendown()

    susceptible_turtle = turtle.Turtle()
    susceptible_turtle.pencolor('blue')
    susceptible_turtle.speed(1)
    susceptible_turtle.penup()
    susceptible_turtle.goto(OFFSET_TURTLE_X, OFFSET_TURTLE_Y + susceptible[0]*SCALE_TURTLE_Y)
    susceptible_turtle.pendown()

    for i in range(len(recovery)):
        recovery_turtle.goto(i*SCALE_TURTLE_X + OFFSET_TURTLE_X,
                             recovery[i]*SCALE_TURTLE_Y + OFFSET_TURTLE_Y)
        infected_turtle.goto(i * SCALE_TURTLE_X + OFFSET_TURTLE_X,
                             infected[i] * SCALE_TURTLE_Y + OFFSET_TURTLE_Y)
        susceptible_turtle.goto(i * SCALE_TURTLE_X + OFFSET_TURTLE_X,
                             susceptible[i] * SCALE_TURTLE_Y + OFFSET_TURTLE_Y)
    turtle.done()


def main():

    results = simulate_ode(
        transmission_rate=3,
        recovery_rate=0.1,
        initial_percent_infected=0.1,
        max_t=40)

    turtle_print_results(results)
    print(f'Maximum peak was {results["peak_infected"]}\nNumber infected was {results["total_recovered"]}')

if __name__ == '__main__':
    main()
