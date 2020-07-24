from django.shortcuts import render, redirect
from django.views import View
from django.http import HttpResponse


class WelcomePageView(View):
    def get(self, request, *args, **kwargs):
        return HttpResponse("<h2>Welcome to the Hypercar Service!</h2>")


class MenuPageView(View):
    def get(self, request, *args, **kwargs):
        return render(request, "tickets/menu.html")


number = 1
number_to_remove = None

line_of_cars = {"change_oil": {"queue": [], "time": 2}, "inflate_tires": {"queue": [], "time": 5},
                "diagnostic": {"queue": [], "time": 30}}


def get_estimated_time(operation):
    global line_of_cars
    estimated_time = 0
    if operation in line_of_cars:
        change_oil_time = len(line_of_cars["change_oil"]["queue"]) * line_of_cars["change_oil"]["time"]
        inflate_tires_time = len(line_of_cars["inflate_tires"]["queue"]) * line_of_cars["inflate_tires"]["time"]
        diagnostic_time = len(line_of_cars["diagnostic"]["queue"]) * line_of_cars["diagnostic"]["time"]
        if operation == "change_oil":
            estimated_time = change_oil_time
        elif operation == "inflate_tires":
            estimated_time = change_oil_time + inflate_tires_time
        elif operation == "diagnostic":
            estimated_time = change_oil_time + inflate_tires_time + diagnostic_time
        line_of_cars[operation]["queue"].append(number)
    return estimated_time


def remove_next():
    global line_of_cars
    res = None
    if len(line_of_cars["change_oil"]["queue"]):
        res = line_of_cars["change_oil"]["queue"].pop(0)
    elif len(line_of_cars["inflate_tires"]["queue"]):
        res = line_of_cars["inflate_tires"]["queue"].pop(0)
    elif len(line_of_cars["diagnostic"]["queue"]):
        res = line_of_cars["diagnostic"]["queue"].pop(0)
    return res


class TicketPageView(View):
    def get(self, request, *args, **kwargs):
        global number
        global line_of_cars
        ticket_number = number
        estimated_time = 0
        if "service_name" in kwargs:
            operation = kwargs["service_name"]
            estimated_time = get_estimated_time(operation)
            number += 1
        return render(request, "tickets/ticket.html",
                      context={"ticket_number": ticket_number, "minutes_to_wait": estimated_time})


class ProcessingPageView(View):
    def get(self, request, *args, **kwargs):
        global line_of_cars
        return render(request, "tickets/processing.html",
                      context={"change_oil_count": len(line_of_cars["change_oil"]["queue"]),
                               "inflate_tires_count": len(line_of_cars["inflate_tires"]["queue"]),
                               "diagnostic_count": len(line_of_cars["diagnostic"]["queue"])})

    def post(self, request, *args, **kwargs):
        global number_to_remove
        number_to_remove = remove_next()
        return redirect(f"/next")


class NextTicketView(View):
    def get(self, request, *args, **kwargs):
        if number_to_remove is None:
            return render(request, "tickets/next_ticket.html")
        else:
            return render(request, "tickets/next_ticket.html", context={"next_number": number_to_remove})
