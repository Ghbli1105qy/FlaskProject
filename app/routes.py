from flask import render_template, request, jsonify, redirect, url_for, current_app
from app.models import db, User, Devices, SensorData
from app.auth import login_required
from datetime import datetime, timedelta
import json
import pytz
local_tz = pytz.timezone('Asia/Shanghai')
def init_routes(app):

    def get_current_time():
        return datetime.now().astimezone(local_tz)
    @app.route('/')
    def index():
        return redirect(url_for('login_page'))



    @app.route('/dashboard', endpoint='dashboard_page')
    @login_required
    def dashboard():
        devices = Devices.query.all()
        now = datetime.utcnow()
        return render_template('dashboard.html', devices=devices,now=now)

    @app.route('/api/data/<device_id>', methods=['GET'], endpoint='api_get_device_data')
    @login_required
    def get_device_data(device_id):
        try:
            device = Devices.query.get(device_id)
            if not device:
                return jsonify({'error': '设备不存在'}), 404

            data = SensorData.query.filter_by(device_id=device_id) \
                .order_by(SensorData.upload_time.desc()) \
                .limit(100).all()

            return jsonify([{
                'time': d.upload_time.isoformat(),
                'rainfall': d.rainfall,
                'temperature': d.temperature,
                'humidity': d.humidity,
                'battery': d.battery
            } for d in data])

        except Exception as e:
            current_app.logger.error(f"API错误: {str(e)}")
            return jsonify({'error': '服务器内部错误'}), 500

    @app.route('/api/data/timeseries', methods=['GET'], endpoint='api_get_timeseries_data')
    @login_required
    def get_timeseries_data():
        try:
            start = request.args.get('start')
            end = request.args.get('end')
            device_id = request.args.get('device_id')

            if not device_id:
                return jsonify({'error': '缺少设备ID'}), 400

            if not start or not end:
                end_date = datetime.utcnow()
                start_date = end_date - timedelta(days=1)
                start = start_date.isoformat()
                end = end_date.isoformat()

            results = db.session.query(
                db.func.date_trunc('hour', SensorData.upload_time).label('hour'),
                db.func.avg(SensorData.rainfall).label('avg_rainfall')
            ).filter(
                SensorData.device_id == device_id,
                SensorData.upload_time.between(start, end)
            ).group_by(db.func.date_trunc('hour', SensorData.upload_time)
                       ).order_by(db.func.date_trunc('hour', SensorData.upload_time)).all()

            return jsonify([{
                'time': row.hour.isoformat(),
                'rainfall': row.avg_rainfall
            } for row in results])

        except Exception as e:
            current_app.logger.error(f"时间序列API错误: {str(e)}")
            return jsonify({'error': '服务器内部错误'}), 500

    @app.route('/api/data/timeseries/<time_granularity>', methods=['GET'], endpoint='api_get_timeseries_data_granularity')
    @login_required
    def get_timeseries_data_granularity(time_granularity):
        try:
            device_id = request.args.get('device_id')

            if not device_id:
                return jsonify({'error': '缺少设备ID'}), 400

            if time_granularity == '5min':
                trunc_func = db.func.date_trunc('minute', SensorData.upload_time - db.func.mod(db.extract('minute', SensorData.upload_time), 5))
            elif time_granularity == 'hour':
                trunc_func = db.func.date_trunc('hour', SensorData.upload_time)
            elif time_granularity == 'month':
                trunc_func = db.func.date_trunc('month', SensorData.upload_time)
            elif time_granularity == 'year':
                trunc_func = db.func.date_trunc('year', SensorData.upload_time)
            else:
                return jsonify({'error': '不支持的时间粒度'}), 400

            results = db.session.query(
                trunc_func.label('time'),
                db.func.avg(SensorData.rainfall).label('avg_rainfall'),
                db.func.avg(SensorData.temperature).label('avg_temperature'),
                db.func.avg(SensorData.humidity).label('avg_humidity')
            ).filter(
                SensorData.device_id == device_id
            ).group_by(trunc_func
                       ).order_by(trunc_func).all()

            return jsonify([{
                'time': row.time.isoformat(),
                'rainfall': row.avg_rainfall,
                'temperature': row.avg_temperature,
                'humidity': row.avg_humidity
            } for row in results])

        except Exception as e:
            current_app.logger.error(f"时间序列API错误: {str(e)}")
            return jsonify({'error': '服务器内部错误'}), 500

    @app.route('/device/<device_id>', endpoint='device_detail_page')
    @login_required
    def device_detail(device_id):
        device = Devices.query.get_or_404(device_id)
        sensor_data = SensorData.query.filter_by(device_id=device_id) \
            .order_by(SensorData.upload_time.desc()) \
            .limit(100).all()

        # 获取最新的传感器数据
        latest_data = sensor_data[0].to_dict() if sensor_data else {}

        # 提取时间戳、温度、湿度等数据
        timestamps = [data.upload_time.isoformat() if data.upload_time else '' for data in sensor_data]
        temps = [data.temperature or 0 for data in sensor_data]
        humids = [data.humidity or 0 for data in sensor_data]
        rainfalls = [data.rainfall or 0 for data in sensor_data]
        batteries = [data.battery or 0 for data in sensor_data]

        return render_template(
            'device_detail.html',
            device=device,
            sensor_data=sensor_data,
            latest_data=latest_data,
            timestamps=timestamps,
            temps=temps,
            humids=humids,
            rainfalls=rainfalls,
            batteries=batteries
        )

    @app.route('/dashboard_large', endpoint='dashboard_large_page')
    @login_required
    def dashboard_large():
        devices = Devices.query.all()
        return render_template('dashboard_large.html', devices=devices)

    @app.route('/api/sensor-data/<device_id>', methods=['GET'])
    @login_required
    def get_sensor_data(device_id):
        # 获取最近30条数据（可根据需求调整）
        data = SensorData.query.filter_by(device_id=device_id) \
            .order_by(SensorData.upload_time.desc()) \
            .limit(30).all()

        # 按时间排序（最新数据在最后）
        data.reverse()

        return {
            'timestamps': [d.upload_time.isoformat() for d in data],
            'temps': [d.temperature for d in data],
            'humids': [d.humidity for d in data],
            'rainfalls': [d.rainfall for d in data],
            'batteries': [d.battery for d in data]
        }

    @app.route('/api/device-status', methods=['GET'])
    @login_required
    def get_device_status():
        devices = Devices.query.all()
        now = get_current_time()
        timeout_threshold = timedelta(minutes=10)
        status_list = []

        for device in devices:
            if not device.last_seen:
                status = "离线"
                time_diff_minutes = None
            else:
                # 确保last_seen有时区信息
                if device.last_seen.tzinfo is None:
                    last_seen = local_tz.localize(device.last_seen)
                else:
                    last_seen = device.last_seen.astimezone(local_tz)

                # 计算时间差
                time_diff = now - last_seen
                time_diff_minutes = round(time_diff.total_seconds() / 60, 1)

                if time_diff_minutes < 0:
                    status = "离线"
                    current_app.logger.warning(
                        f"设备 {device.id} 时间异常: last_seen={last_seen} 晚于当前时间{now}"
                    )
                else:
                    status = '在线' if time_diff < timeout_threshold else '离线'

            status_list.append({
                'id': device.id,
                'status': status,
                'last_seen': last_seen.isoformat() if device.last_seen else None,
                'time_diff_minutes': time_diff_minutes
            })

        return jsonify(status_list)

    @app.route('/api/upload-data', methods=['POST'])
    @login_required
    def upload_data():
        try:
            data = request.get_json()
            device_id = data.get('device_id')
            device = Devices.query.get(device_id)
            if not device:
                return jsonify({'error': '设备不存在'}), 404

            current_time = get_current_time()
            current_app.logger.debug(f"服务器本地时间: {datetime.now()}")
            current_app.logger.debug(f"转换后的带时区时间: {current_time}")

            # 处理客户端时间（如果提供）
            client_time_str = data.get('client_time')
            if client_time_str:
                try:
                    client_time = datetime.fromisoformat(client_time_str)
                    if client_time.tzinfo is None:
                        client_time = local_tz.localize(client_time)
                    else:
                        client_time = client_time.astimezone(local_tz)

                    if abs((client_time - current_time).total_seconds()) < 300:
                        current_time = client_time
                    else:
                        current_app.logger.warning(f"设备 {device_id} 时间偏差过大，使用服务器时间")
                except Exception as e:
                    current_app.logger.warning(f"设备 {device_id} 时间格式错误: {str(e)}，使用服务器时间")

            device.last_seen = current_time
            db.session.commit()

            sensor_data = SensorData(
                device_id=device_id,
                temperature=data.get('temperature'),
                humidity=data.get('humidity'),
                rainfall=data.get('rainfall'),
                battery=data.get('battery'),
                upload_time=current_time
            )
            db.session.add(sensor_data)
            db.session.commit()

            return jsonify({'message': '数据上传成功'}), 200

        except Exception as e:
            current_app.logger.error(f"数据上传错误: {str(e)}")
            return jsonify({'error': '服务器内部错误'}), 500

