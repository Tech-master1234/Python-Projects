
fetch("http://127.0.0.1:8000/api/storage")
  .then(res => res.json())
  .then(data => {
    const ctx = document.getElementById('storageChart').getContext('2d');
    const categories = Object.keys(data.categories);
    const sizes = Object.values(data.categories).map(bytes => (bytes / (1024 ** 3)).toFixed(2));

    new Chart(ctx, {
      type: 'bar',
      data: {
        labels: categories,
        datasets: [{
          label: 'Size (GB)',
          data: sizes,
          backgroundColor: [
            '#ff6384', '#36a2eb', '#ffcd56', '#4bc0c0',
            '#9966ff', '#ff9f40', '#e7e9ed', '#aaaaaa', '#66bb6a', '#ec407a'
          ],
        }]
      },
      options: {
        responsive: true,
        plugins: {
          legend: { display: false },
          title: {
            display: true,
            text: `Used: ${(data.used / (1024 ** 3)).toFixed(1)} GB / ${(data.total / (1024 ** 3)).toFixed(1)} GB`
          }
        }
      }
    });
  });
