from django.shortcuts import render, redirect
from django.http import Http404
from bokeh.embed import components
from .utils import volume_helper, single_stock, make_candlestick, month_average

def homeview(request):
    """Fucntion based view that renders the graphs
    based on the ticker and graph type selected
    :param request: request
    :return: HTML View
    """
    template_name = 'tickerform.html'
    context = {}
    if request.method == 'GET':
        ticker = request.GET.get('ticker')
        graph = request.GET.get('choice')
        if graph:
            if graph == 'Single Stock':
                plot = single_stock(ticker)
                script, div = components(plot)
                context = {
                    "script": script,
                    "div": div,
                    "ticker": ticker,
                    "graph": graph
                }
                template_name = 'singleview.html'
                return render(request, template_name, context)
            elif graph == 'Candlestick':
                plot = make_candlestick(ticker)
                script, div = components(plot)
                context = {
                    "script": script,
                    "div": div,
                    "ticker": ticker,
                    "graph": graph
                }
                template_name = 'singleview.html'
                return render(request, template_name, context)
            elif graph == 'One Month Average':
                plot = month_average(ticker)
                script, div = components(plot)
                context = {
                    "script": script,
                    "div": div,
                    "ticker": ticker,
                    "graph": graph
                }
                template_name = 'singleview.html'
                return render(request, template_name, context)
    return render(request, template_name, context)
