// dynamic_charts.js
let envChart = null;
let batteryChart = null;
const deviceId = "{{ device.id }}";

async function updateCharts() {
    try {
        const response = await fetch(`/api/sensor-data/${deviceId}`);
        if (!response.ok) throw new Error('数据获取失败');

        const data = await response.json();

        // 更新环境图表
        envChart.data.labels = data.timestamps;
        envChart.data.datasets[0].data = data.temps;
        envChart.data.datasets[1].data = data.humids;
        envChart.data.datasets[2].data = data.rainfalls;
        envChart.update();

        // 更新电池图表
        batteryChart.data.labels = data.timestamps;
        batteryChart.data.datasets[0].data = data.batteries;
        batteryChart.update();

    } catch (error) {
        console.error('图表更新错误:', error);
    }
}

document.addEventListener('DOMContentLoaded', async function () {
    // 初始化图表和定时器的代码...
    //（完整代码见下方）
});