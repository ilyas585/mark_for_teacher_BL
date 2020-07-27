var data = document.getElementById('data').textContent;
    var data2 = JSON.parse(data)
	var i;
	let data_int = []
	let _int = []
	let data_com = []
	let _com = []
	let data_beh = []
	let _beh = []
	for (i = 0; i < data2.lesson_interest.length; ++i)
	{
		_int.push(data2.lesson_interest[i][0]);
		data_int.push(data2.lesson_interest[i][1]);
	}
	for (i = 0; i < data2.lesson_com.length; ++i)
	{
		_com.push(data2.lesson_com[i][0]);
		data_com.push(data2.lesson_com[i][1]);
	}
	for (i = 0; i < data2.teacher_behavior.length; ++i)
	{
		_beh.push(data2.teacher_behavior[i][0]);
		data_beh.push(data2.teacher_behavior[i][1]);
	}
var ctx = document.getElementById('myChart').getContext('2d');
var myChart = new Chart(ctx, {
    type: 'line',
    fill: false,
    data: {
        labels:data_int,
        fill: false,
        datasets: [{
           fill: false,
            label: 'Понятность урока',
            data: _int,
			pointBackgroundColor:'rgba(32, 0, 255, 1)',
            borderColor: ['rgba(32, 0, 255, 1)'],
            borderWidth: 4,
			pointRadius: 7
        },
		{
			labels:data_com,
           fill: false,
            label: 'Интересность урока',
            data: _com,
			pointBackgroundColor:'rgba(255, 0, 1, 1)',
            borderColor: ['rgba(255, 0, 1, 1)'],
            borderWidth: 4,
			pointRadius: 7
        },
		{
			labels:data_beh,
           fill: false,
            label: 'Поведение учителя',
            data: _beh,
			pointBackgroundColor:'rgba(1, 255, 1, 1)',
            borderColor: ['rgba(1, 255, 1, 1)'],
            borderWidth: 4,
			pointRadius: 7
        }
		
		]
    },
    options: {
        scales: {
            yAxes: [{
                ticks: {
                    fill: false,
                    beginAtZero: true
                }
            }]
        }
    }
});