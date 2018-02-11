from pyramid.view import view_config

from ..models.album import Album


class AlbumViews:
    def __init__(self, request):
        # Used by the before_insert and before_update event listeners
        request.dbsession.info['username'] = request.user.username
        self.request = request

    @view_config(route_name='api-photo-count-by-album', renderer='json')
    def api_photo_count_by_album(self):
        counts = Album().get_photo_counts_by_album(self.request.dbsession)

        labels = []
        data = []
        for item in counts:
            labels.append(item[0])
            data.append(item[1])

        result_size = len(labels)

        backgroung_colors = [
            'rgba(255, 99, 132,  0.2)',
            'rgba(54,  162, 235, 0.2)',
            'rgba(255, 206, 86,  0.2)',
            'rgba(75,  192, 192, 0.2)',
            'rgba(153, 102, 255, 0.2)',
            'rgba(255, 159, 64,  0.2)'
        ]

        border_colors = [
            'rgba(255, 99, 132,  1)',
            'rgba(54,  162, 235, 1)',
            'rgba(255, 206, 86,  1)',
            'rgba(75,  192, 192, 1)',
            'rgba(153, 102, 255, 1)',
            'rgba(255, 159, 64,  1)'
        ]

        chart = {
            'type': 'bar',
            'data': {
                'labels': labels,
                'datasets': [{
                    'data': data,
                    'backgroundColor': backgroung_colors[:result_size],
                    'borderColor': border_colors[:result_size],
                    'borderWidth': 1
                }]
            },
            'options': {
                'title': {
                    'display': False
                },
                'legend': {
                    'display': False
                },
                'scales': {
                    'yAxes': [{
                        'ticks': {
                            'beginAtZero': True
                        }
                    }]
                }
            }
        }

        return chart
