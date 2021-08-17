<template>
	<div class="maintenancePlanAdd">
		<el-row>
			<el-tag type size="medium">
				<i class="el-icon-discount" round>标注结果：</i>
			</el-tag>
			<el-button size="mini" style="float:right" type="primary" @click="save">保存当前标注</el-button>
			<el-tag type size="medium" style="margin-left: 10px;">{{taglabel.name}}</el-tag>
		</el-row>
		<div class="panel-body" style="margin-top:20px">
			<el-card>
				<div style="position: relative;" id="waveformmm" ref="waveformmm">
					<div id="wave-timelineee" ref="wave-timelineee">
					</div>
				</div>
				<div style="margin-top: 10px;">
					<div style=" display: flex;">
						<el-button style="height: 40px;margin-right:3px ;" type="primary" @click="rew">后退</el-button>
						<el-button style="height: 40px;margin-right:3px ;" type="primary" @click="speek">前进</el-button>
						<el-button style="height: 40px;margin-right:10px ;" type="primary" @click="replay">重放
						</el-button>
						<el-tooltip style="margin-right:200px ;" class="item" effect="dark" content="指定播放"
							placement="bottom">
							<el-popover placement="top" width="200" trigger="click">
								<el-input v-model="appointTime" placeholder="请输入内容" class="input-with-select">
									<el-button slot="append" @click="appointPlay">播放</el-button>
								</el-input>
								<el-button style="color: #409EFF;" slot="reference">
									指定播放
								</el-button>
							</el-popover>
						</el-tooltip>
						<div style=" display: flex;flex:1">
							<img src="./img/zoom_minus.png" style="max-width:100px;height:50px;margin-right: 10px; "
								class="head_pic" />
							<el-tooltip content="放大缩小">

								<el-slider v-model="zoomval" id="zoomslider" style="flex: 1;" class="zoomslider"
									@change="zzoom" />

							</el-tooltip>
							<img src="./img/zoom_plus.png" style="max-width:100px;height:50px;margin-left: 10px;"
								class="head_pic" />
						</div>
					</div>
					<el-button style=" background-color: #F56C6C;color: white ;" @click="deleteone">
						删除
					</el-button>
					<el-tooltip content="删除所有当前分割">
						<el-button style=" background-color: #F56C6C;color: white ;" @click="clearall">
							清除所有
						</el-button>
					</el-tooltip>
				</div>
			</el-card>
			<div class="demo">

				<el-carousel ref="carousel" :initial-index="1" indicator-position="none" :autoplay="false"
					arrow="always" style="width:810px" height="50px" @change="preCarouselChange">

					<el-carousel-item v-for="item in 3" :key="item"></el-carousel-item>
					<!-- <canvas id="canvas" :width="width" :height="height" style="position: absolute; z-index: 9"></canvas> -->
				</el-carousel>
				<div>
					<!-- <el-button type="primary" @click="rew">后退</el-button>
					<el-button type="primary" @click="plays">
						<i class="el-icon-video-play"></i>
						播放 /
						<i class="el-icon-video-pausee"></i>
						暂停
					</el-button>
					<el-button type="primary" @click="speek">前进</el-button> -->

					<!-- <span style="border: 2px solid #2f4f4f;margin-left: 8px;margin-right: 4px" /> -->
					<!-- <el-tooltip class="item" effect="dark" content="音量" placement="bottom">
						<el-popover placement="top-start" trigger="click" style="min-width: 38px;margin-left: 10px">
							<div class="block" style="width: 42px">
								<el-slider v-model="value" vertical height="100px" @change="setVolume" />
							</div>
							<el-button slot="reference" circle>
								音量
							</el-button>

						</el-popover>
					</el-tooltip> -->

					<!-- <el-tooltip class="item" effect="dark" content="播放倍速" placement="bottom">
				<el-popover placement="top" width="220" trigger="click" style="margin-left: 10px">
					<el-input-number v-model="ds" width="180" :precision="2" :step="0.1" :min="0.5" :max="2"
						@change="DoubleSpeed" />
					<el-button slot="reference" round>
						{{ ds +' X' }}
					</el-button>
				</el-popover>
			</el-tooltip> -->
				</div>
			</div>
		</div>
		<img src="./assets/icons/del.png" id="del_image" v-show="false" />
	</div>
</template>
<script>
	import bus from './bus.js'
	import {
		alertBox
	} from '@/utils/alertBox.js'
	import WaveSurfer from 'wavesurfer.js'
	import CursorPlugin from 'wavesurfer.js/dist/plugin/wavesurfer.cursor.js'
	import Timeline from 'wavesurfer.js/dist/plugin/wavesurfer.timeline.js'
	import RegionsPlugin from 'wavesurfer.js/dist/plugin/wavesurfer.regions.js';

	export default {
		name: 'DetectionPage',
		props: {
			noteDatasetInfo: {
				type: Object,
				default: null,
			},
			start_img: {},
		},
		data() {
			return {
				regionlist: {},
				width: 800,
				height: 450,
				picTableData: [],
				canvas: {},
				src: '',
				waveform: null,
				// 指定播放功能的播放时间点
				appointTime: 1,
				// 播放倍速
				ds: 1.00,
				// 设置音量
				zoomval: 0,
				value: 0,
				current_pos: {
					top: 0,
					left: 0,
					scale: 1
				},
				currentImg: {
					offset: 0,
					order: 0,
					id: '',
					src: '',
					rel_pic_lab: [],
				},
				img: {},
				group_num: 8,
				changeTag: false,
				check: false,
				rect: [],
				x: '',
				y: '',
				mouseFrom: {},
				mouseTo: {},
				// drawType: null, //当前绘制图像的种类
				canvasObjectIndex: 0,
				drawWidth: 2, //笔触宽度
				color: '#E34F51', //画笔颜色
				drawingObject: null, //当前绘制对象
				moveCount: 1, //绘制移动计数器
				doDrawing: false, // 绘制状态
				select_obj: '', // 当前是否有矩形框被单击
				taglabel: {
					label_id: '',
					name: '-',
					color: '',
					content: '',
					id: ''
				},
				detail_info: [],
				baseurl: this.$store.state.baseurl,
			}
		},
		watch: {
			// drawType() {
			//   this.canvas.selection = !this.drawType
			// },
			width() {
				this.canvas.setWidth(this.width)
			},
			height() {
				this.canvas.setHeight(this.height)
			},
			noteDatasetInfo(newVal) {
				this.noteDatasetInfo = newVal
			},
			start_img(newVal) {
				this.start_img = newVal
				this.currentImg = newVal
				this.currentImg.offset = newVal.order
				this.currentImg.order = newVal.order % this.group_num
				this.src = this.currentImg.src
				this.showImage(this.src)
				this.sendToNote()
			},
		},
		methods: {
			// 保存标注
			save(instruct) {
				let that = this

				//if (!this.changeTag) {
					//if (instruct.type === 'carouselChange') {
						//that.carouselChange(instruct.args1, instruct.args2, this.currentImg.src)
					//}
					//if (instruct.type === 'changeImg') {
						//that.currentImg = {
							//offset: instruct.args1.offset,
							//order: instruct.args1.order,
							//id: instruct.args1.id,
							//src: instruct.args1.src,
						//}
						//that.showImage(that.currentImg.src)
					//}
					//if (instruct.type === 'preGroupImg') {
						//bus.$emit('saveOk', instruct)
					//}
					//if (instruct.type === 'nextGroupImg') {
						//bus.$emit('saveOk', instruct)
					//}
					//return
				//}
				this.changeTag = false
				var data = {}
				data.note_infos = []
				this.check = false
				for (var item in this.wavesurfer.regions.list) {
						var info = {}
            info.content = {}
            var tmp = {}
            info.label_id = this.wavesurfer.regions.list[item].tag_id
						tmp.start = this.wavesurfer.regions.list[item].start
						tmp.end = this.wavesurfer.regions.list[item].end
            info.content = tmp
            data.note_infos.push(info)
        }
				if (that.check) return
				data.note_infos = JSON.stringify(data.note_infos)
				data.picture_id = this.currentImg.id
				data = this.$qs.stringify(data)
				//添加标签
				this.$api.data_note.save_note_info(data).then((response) => {
				  console.log("saving")
					if (response.data.msg === 'error') {
						alertBox(response.data.data, 'error', that, '标注失败')
						if (instruct.type === 'changeImg') {
							instruct.args1 = that.currentImg.order
							bus.$emit('saveFail', instruct)
						}
						return false
					} else {
						that.$message({
							type: 'success',
							message: '标注成功!',
						})
						//保存成功后根据type类型调用函数
						if (instruct.type === 'carouselChange') {
							that.carouselChange(instruct.args1, instruct.args2, this.currentImg.src)
						}
						if (instruct.type === 'changeImg') {
							that.currentImg = {
								offset: instruct.args1.offset,
								order: instruct.args1.order,
								id: instruct.args1.id,
								src: instruct.args1.src,
							}
							that.showImage(that.currentImg.src)
						}
						if (instruct.type === 'preGroupImg') {
							bus.$emit('saveOk', instruct)
						}
						if (instruct.type === 'nextGroupImg') {
							bus.$emit('saveOk', instruct)
						}
						return true
					}
				})
			},
			showImage(src) {
				let that = this
				var path = this.baseurl + src;
				var data = {
					picture_id: that.currentImg.id
				}

				function formatTimeCallback(seconds, pxPerSec) {
					seconds = Number(seconds);
					var minutes = Math.floor(seconds / 60);
					seconds = seconds % 60;

					// fill up seconds with zeroes
					var secondsStr = Math.round(seconds).toString();
					if (pxPerSec >= 25 * 10) {
						secondsStr = seconds.toFixed(2);
					} else if (pxPerSec >= 25 * 1) {
						secondsStr = seconds.toFixed(1);
					}

					if (minutes > 0) {
						if (seconds < 10) {
							secondsStr = '0' + secondsStr;
						}
						return `${minutes}:${secondsStr}`;
					}
					return secondsStr;
				};

				function timeInterval(pxPerSec) {
					var retval = 1;
					if (pxPerSec >= 25 * 100) {
						retval = 0.01;
					} else if (pxPerSec >= 25 * 40) {
						retval = 0.025;
					} else if (pxPerSec >= 25 * 10) {
						retval = 0.1;
					} else if (pxPerSec >= 25 * 4) {
						retval = 0.25;
					} else if (pxPerSec >= 25) {
						retval = 1;
					} else if (pxPerSec * 5 >= 25) {
						retval = 5;
					} else if (pxPerSec * 15 >= 25) {
						retval = 15;
					} else {
						retval = Math.ceil(0.5 / pxPerSec) * 60;
					}
					return retval;
				};

				function primaryLabelInterval(pxPerSec) {
					var retval = 1;
					if (pxPerSec >= 25 * 100) {
						retval = 10;
					} else if (pxPerSec >= 25 * 40) {
						retval = 4;
					} else if (pxPerSec >= 25 * 10) {
						retval = 10;
					} else if (pxPerSec >= 25 * 4) {
						retval = 4;
					} else if (pxPerSec >= 25) {
						retval = 1;
					} else if (pxPerSec * 5 >= 25) {
						retval = 5;
					} else if (pxPerSec * 15 >= 25) {
						retval = 15;
					} else {
						retval = Math.ceil(0.5 / pxPerSec) * 60;
					}
					return retval;
				};

				function secondaryLabelInterval(pxPerSec) {
					// draw one every 10s as an example
					return Math.floor(10 / timeInterval(pxPerSec));
				};
				// console.log(path);
				// if (this.wavesurfer != null) {
				// 	// this.wavesurfer.clearRegions()
				// }
				// //适配大小
				// var r;
				// console.log(this.regionlist[path])
				// if (this.regionlist[path] == undefined || this.regionlist[path] == {}) {
				// 	console.log("list is empty")
				// 	r = new RegionsPlugin.create({
				// 		// plugin options ...
				// 		regions: [

				// 		],
				// 		dragSelection: {
				// 			slop: 5
				// 		}
				// 	})
				// } else {
				// 	console.log("list isn't empty")
				// 	r = this.regionlist[path]
				// }
				// console.log(typeof(path))
				this.$nextTick(() => {
					// console.log(WaveSurfer)
					if (this.wavesurfer == null) {
						this.wavesurfer = WaveSurfer.create({
							// 应该在其中绘制波形的CSS选择器或HTML元素。这是唯一必需的参数。
							container: document.querySelector('#waveformmm'),
							// 光标的填充颜色，指示播放头的位置。
							cursorColor: '#2C3E50',
							// 更改波形容器的背景颜色。
							backgroundColor: 'white',
							// 光标后的波形填充颜色。
							waveColor: 'blue',
							height: '200',
							// 光标后面的波形部分的填充色。当progressColor和waveColor相同时，完全不渲染进度波
							progressColor: '#66B1FF',
							backend: 'MediaElement',
							// 音频播放时间轴
							mediaControls: true,
							// 播放音频的速度
							audioRate: '1',
							//fillparent:false,
							// 插件：此教程配置了光标插件和时间轴插件
							plugins: [
								// 时间轴插件
								Timeline.create({
									container: '#wave-timelineee',
									formatTimeCallback: formatTimeCallback,
									timeInterval: timeInterval,
									primaryLabelInterval: primaryLabelInterval,
									secondaryLabelInterval: secondaryLabelInterval,
									primaryColor: 'blue',
									secondaryColor: 'red',
									primaryFontColor: 'blue',
									secondaryFontColor: 'red',

								}),
								RegionsPlugin.create({
									// plugin options ...
									regionsMinLength: 0.1,
									regions: [

									],
									dragSelection: {
										slop: 5
									}
								}),
								// 光标插件
								CursorPlugin.create({
									showTime: true,
									opacity: 1,
									customShowTimeStyle: {
										'background-color': '#0098FF',
										color: '#fff',
										padding: '4px',
										'font-size': '10px',

									},

								}),

							],

						});
						//this.wavesurfer.cursor.wrapper = this.wavesurfer.container
						this.wavesurfer.on('error', function(e) {
							console.warn(e);
						});

					} else {
						this.wavesurfer.regions.clear();
						//this.wavesurfer.regions.list=this.regionlist[path];
						// console.log(this.regionlist[path]);
						for (var item in this.regionlist[path]) {
							// console.log(item);
							// console.log(this.regionlist[path][item]);
							this.wavesurfer.regions.add(this.regionlist[path][item]);

						}

					}
					//console.log((this.wavesurfer.regions.list));
					for (var item in this.wavesurfer.regions.list) {
						//console.log(item);
						//console.log(typeof(item));
						//console.log(this.wavesurfer.regions.list[item].start);
						//console.log(this.wavesurfer.regions.list[item].end);

					}
					//console.log(typeof(this.wavesurfer.regions.list));
					console.log(this.wavesurfer.cursor['cursor']);
					console.log(this.wavesurfer.regions.list);
					this.wavesurfer.load(path);
					// this.value = this.wavesurfer.getVolume() * 100
				})

			},
			deleteone() {
				if (this.wavesurfer.regions.getCurrentRegion() == null) {
					alertBox('请选定时间段', 'warning', this);
				} else {
					//console.log(this.wavesurfer.regions.getCurrentRegion());
					// this.wavesurfer.regions.getCurrentRegion()['color'] = 'rgba(255, 23, 26, 0.1)';
					// console.log(this.wavesurfer.regions.getCurrentRegion().click())
					// this.wavesurfer.regions.getCurrentRegion()['start'] = '2';
					//this.wavesurfer.load(this.baseurl+this.currentImg.src)
					//console.log(this.wavesurfer.regions.getCurrentRegion()['color']);
					//this.wavesurfer.load(this.baseurl+this.currentImg.src);
					this.wavesurfer.regions.getCurrentRegion().remove();
					this.regionlist[this.baseurl + this.currentImg.src] = {
						...this.wavesurfer.regions.list
					};

				}
			},
			saveRegion() {

			},
			plays() {
				this.wavesurfer.playPause()
			},
			// 后退，
			rew() {
				this.wavesurfer.skip(-3)
			},
			// 前进，
			speek() {
				this.wavesurfer.skip(3)
			},
			// 重放
			replay() {
				this.wavesurfer.stop()
			},
			// 设置音量：
			setVolume(val) {
				this.wavesurfer.setVolume(val / 100)
			},
			// 指定播放
			appointPlay() {
				this.wavesurfer.play([this.appointTime, ])
			},
			zzoom(val) {

				console.log("here")
				this.wavesurfer.zoom(this.zoomval / 0.01);

				console.log(this.zoomval / 0.01)
			},
			clearall() {
				this.wavesurfer.regions.clear();
				this.regionlist[this.baseurl + this.currentImg.src] = {};
			},
			preCarouselChange(key1, key2) {

				var info = {}
				info.type = 'carouselChange'
				info.args1 = key1
				info.args2 = key2
				this.save(info)
			},
			carouselChange(key1, key2, src) {
				var path = this.baseurl + src;
				let index = this.currentImg.order //% this.group_num
				if (key1 === 2) {
					console.log('向右滑动，下一个图片')
					this.regionlist[path] = {
						...this.wavesurfer.regions.list
					};
					if (index === this.picTableData.length - 1) bus.$emit('nextPicTable', index)
					else {
						this.currentImg = this.picTableData[index + 1]
						this.showImage(this.currentImg.src)
						bus.$emit('nextPic', index + 1)
					}
				}
				if (key1 === 0) {
					console.log('向左滑动，上一个图片')
					this.regionlist[path] = {
						...this.wavesurfer.regions.list
					};
					if (index === 0) bus.$emit('prePicTable', index)
					else {
						this.currentImg = this.picTableData[index - 1]
						this.showImage(this.currentImg.src)
						bus.$emit('prePic', index - 1)
					}
				}
				this.$refs.carousel.setActiveItem(1)
			},
			setObjStatic() {
				if (this.select_obj === '') return
				this.select_obj.set({
					isSelect: false,
					hasBorders: false,
					hasControls: false,
					lockMovementX: true,
					lockMovementY: true,
					lockScalingX: true,
					lockScalingY: true,
				})
				this.select_obj.hidden_tag()
				if (!this.select_obj.hasTag) this.select_obj.show_warning()
			},
			setObjDynamic() {
				if (this.select_obj === '') return
				this.select_obj.hidden_tag()
				this.select_obj.set({
					isSelect: true,
					hasBorders: true,
					hasControls: true,
					lockMovementX: false,
					lockMovementY: false,
					lockScalingX: false,
					lockScalingY: false,
				})
				if (!this.select_obj.hasTag) this.select_obj.hidden_warning()
				// this.canvas.setActiveObject(this.select_obj)
				this.select_obj.show_tag(true)
			},
			sendToNote() {
				let info = {}
				info.img_offset = this.currentImg.offset
				info.img_order = this.currentImg.order
				info.show_type = this.start_img.show_type
				bus.$emit('sendToNote', info)
			},
			// // 开始绘制时，指定绘画种类
			// drawTypeChange(e) {
			//   this.drawType = e
			// },
			// 鼠标按下时触发
			mousedown(e) {
				// 记录鼠标按下时的坐标
				var xy = e.pointer || this.transformMouse(e.e.offsetX, e.e.offsetY)
				this.mouseFrom.x = xy.x
				this.mouseFrom.y = xy.y
				this.doDrawing = true
				this.isClick = true
				if (this.select_obj !== '') {
					if (
						this.mouseFrom.x > this.select_obj.left - 20 &&
						this.mouseFrom.x < this.select_obj.left + this.select_obj.width * this
						.select_obj.scaleX + 20 &&
						this.mouseFrom.y > this.select_obj.top - 20 &&
						this.mouseFrom.y < this.select_obj.top + this.select_obj.height * this
						.select_obj.scaleY + 20
					)
						return
					else {
						console.log('超出边界！')
						// console.log(this.select_obj)
						this.setObjStatic()
						this.select_obj = ''
					}
				}
			},
			// 鼠标松开执行
			mouseup(e) {
				if (this.isClick) {
					if (this.canvas.getActiveObjects().length > 0) {
						if (this.select_obj !== '') {
							// console.log('清空上次')
							this.setObjStatic()
						}
						this.select_obj = this.canvas.getActiveObjects()[0]
						// console.log('重新设置')
						this.setObjDynamic()
					} else {
						// console.log('没点到矩形')
						this.setObjStatic()
						this.select_obj = ''
					}
				} //else console.log('移动事件')
				if (this.drawingObject) {
					this.select_obj = this.drawingObject
					this.canvas.setActiveObject(this.select_obj)
					this.setObjDynamic()
				}
				var xy = e.pointer || this.transformMouse(e.e.offsetX, e.e.offsetY)
				this.mouseTo.x = xy.x
				this.mouseTo.y = xy.y
				this.drawingObject = null
				this.moveCount = 1
				this.doDrawing = false
			},

			//鼠标移动过程中已经完成了绘制
			mousemove(e) {
				if (this.moveCount % 2 && !this.doDrawing) {
					//减少绘制频率
					return
				}
				this.isClick = false
				this.moveCount++
				var xy = e.pointer || this.transformMouse(e.e.offsetX, e.e.offsetY)
				this.mouseTo.x = xy.x
				this.mouseTo.y = xy.y
				if (this.select_obj !== '') return
				this.drawing(e)
			},
			//伸缩时边框大小不变
			scaling(e) {
				const o = e.target
				if (!o.strokeWidthUnscaled && o.strokeWidth) {
					o.strokeWidthUnscaled = o.strokeWidth
				}
				if (o.strokeWidthUnscaled) {
					o.strokeWidth = o.strokeWidthUnscaled / Math.max(o.scaleX, o.scaleY)
				}
			},
			deleteObj() {
				this.canvas.getActiveObjects().map((item) => {
					this.canvas.remove(item)
				})
			},
			transformMouse(mouseX, mouseY) {
				return {
					x: mouseX / 1,
					y: mouseY / 1
				}
			},
			drawing(e) {
				if (this.drawingObject) {
					this.canvas.remove(this.drawingObject)
				}
				var rectOptions = null
				var left = this.mouseFrom.x > this.mouseTo.x ? this.mouseTo.x : this.mouseFrom.x,
					top = this.mouseFrom.y > this.mouseTo.y ? this.mouseTo.y : this.mouseFrom.y,
					mouseFrom = this.mouseFrom,
					mouseTo = this.mouseTo

				rectOptions = {
					id: 'goal_obj',
					hasTag: false,
					isSelect: false,
					left: left,
					top: top,
					width: Math.abs(mouseTo.x - mouseFrom.x), //矩形的宽度
					height: Math.abs(mouseTo.y - mouseFrom.y), //矩形的高度
					fill: this.color,
					stroke: this.color,
					// fill: 'rgba(255, 255, 255, 0)',
				}

				if (rectOptions) {
					// canvasObject.index = getCanvasObjectIndex();\
					const textOptions = {
						width: 0,
						fill: 'black',
						opacity: 0.8,
						fontSize: 12,
					}
					rectOptions.width = rectOptions.width > 0 ? rectOptions.width : 1
					rectOptions.height = rectOptions.height > 0 ? rectOptions.height : 1
					var rectWithText = new fabric.RectWithText(rectOptions, textOptions, '')
					this.canvas.add(rectWithText) //.setActiveObject(canvasObject)
					this.drawingObject = rectWithText
					this.changeTag = true
				}
			},
		},
		created() {
			let that = this
			var dic = new Array();
			this.regionlist = dic;
			console.log(typeof(this.regionlist))
			bus.$on('sendToDetection', (note) => {
				// console.log(note)
				if (that.wavesurfer.regions.getCurrentRegion() != null) {
					// that.changeTag = true
					// that.select_obj.hasTag = true
					// that.select_obj.label_id = note.id
					// that.select_obj.text.set({
					// 	text: note.name,
					// 	width: 0
					// })
					// that.select_obj.set({
					// 	fill: note.color,
					// 	stroke: note.color
					// })
					// that.canvas.renderAll()
					that.taglabel=note
					console.log(that.taglabel);
					that.wavesurfer.regions.getCurrentRegion()['tag']=that.taglabel.name;
					that.wavesurfer.regions.getCurrentRegion()['tag_id']=that.taglabel.id;
					var RGBA = "rgba(" + parseInt("0x" + that.taglabel.color.slice(1, 3)) + "," + parseInt("0x" + that.taglabel.color.slice(3, 5)) + "," + parseInt( "0x" + that.taglabel.color.slice(5, 7)) + ",0.2)";	
					that.wavesurfer.regions.getCurrentRegion()['color']=RGBA;
					//console.log(that.wavesurfer.regions.getCurrentRegion()['element']['title'])
					//that.wavesurfer.regions.getCurrentRegion()['element']['title']=that.taglabel.name ;
					that.wavesurfer.load(that.baseurl+that.currentImg.src);
					
				}else{
					alertBox('请选定时间段', 'warning', this);
				}
			})
			bus.$on('updatePicTableData', (data) => {
				that.picTableData = data.picTableData
				if (data.if_new_pic) {
					//查找该图片标签等信息（详细信息）简单信息就是列表，只包括数据库单个表的信息，详细信息指的是标签等信息
					that.currentImg = {
						offset: that.picTableData[0].offset,
						order: that.picTableData[0].order,
						id: that.picTableData[0].id,
						src: that.picTableData[0].src,
					}
					that.showImage(that.currentImg.src)
				}
			})
			bus.$on('savePic', (data) => {
				console.log(data)
				that.save(data)
			})
		},
		mounted() {
			this.canvas = new fabric.Canvas('canvas', {
				uniScaleTransform: true,
				preserveObjectStacking: true,
			})
			this.canvas.selection = false
			// this.canvas.preserveObjectStacking = false
			this.canvas.selectionColor = 'rgba(0,0,0,0.05)'
			this.canvas.on('mouse:down', this.mousedown)
			this.canvas.on('mouse:move', this.mousemove)
			this.canvas.on('mouse:up', this.mouseup)
			this.canvas.on('object:scaling', this.scaling)
			this.del_img = document.getElementById('del_image')
			// this.canvas.on('selection:created', (e) => {
			//   const o = e.target
			//   o.text.moveTo(o.getZIndex() + 999)
			//   console.log('show index')
			//   console.log(o.getZIndex())
			//   console.log(o.text.getZIndex())
			// })
			let that = this

			fabric.Object.prototype.getZIndex = function() {
				return that.canvas.getObjects().indexOf(this)
			}

			fabric.Canvas.prototype.moveToLayer = function(object, position) {
				while (object.getZIndex() > position) {
					this.sendBackwards(object)
				}
			}

			document.onkeydown = (e) => {
				// 键盘 delect删除所选元素
				if (e.keyCode == 46) {
					this.deleteObj()
				}
				// ctrl+z 删除最近添加的元素
				// if (e.keyCode == 90 && e.ctrlKey) {
				//   this.canvas.remove(
				//     this.canvas.getObjects()[this.canvas.getObjects().length - 1]
				//   );
				// }
			}

			fabric.RectWithText = fabric.util.createClass(fabric.Rect, {
				type: 'rectWithText',
				text: null,
				del_img: null,
				delOffsetLeft: 0,
				delOffsetTop: 0,
				textOffsetLeft: 0,
				textOffsetTop: 0,
				_prevObjectStacking: null,
				_prevAngle: 0,

				recalcTextPosition: function() {
					const sin = Math.sin(fabric.util.degreesToRadians(this.angle))
					const cos = Math.cos(fabric.util.degreesToRadians(this.angle))
					const newTop = sin * this.textOffsetLeft + cos * this.textOffsetTop
					const newLeft = cos * this.textOffsetLeft - sin * this.textOffsetTop
					const rectLeftTop = this.getPointByOrigin('left', 'top')
					this.text.set('left', rectLeftTop.x + newLeft)
					this.text.set('top', rectLeftTop.y + newTop)
				},

				recalcDelPosition: function() {
					const sin = Math.sin(fabric.util.degreesToRadians(this.angle))
					const cos = Math.cos(fabric.util.degreesToRadians(this.angle))
					const newTop = sin * this.delOffsetLeft + cos * this.delOffsetTop
					const newLeft = cos * this.delOffsetLeft - sin * this.delOffsetTop
					const rectLeftTop = this.getPointByOrigin('left', 'top')
					this.del_img.set('left', rectLeftTop.x + newLeft)
					this.del_img.set('top', rectLeftTop.y + newTop)
				},

				initialize: function(rectOptions, textOptions, text) {
					let rect = this
					rectOptions.strokeWidth = 1
					rectOptions.opacity = 0.3
					rectOptions.hasBorders = false
					rectOptions.hasControls = false
					rectOptions.lockMovementX = true
					rectOptions.lockMovementY = true
					rectOptions.lockRotation = true
					rectOptions.lockScalingX = true
					rectOptions.lockScalingY = true
					rectOptions.noScaleCache = false
					rectOptions.transparentCorners = false
					rectOptions.cornerColor = 'blue'
					rectOptions.cornerStrokeColor = 'red'
					rectOptions.borderColor = 'red'
					rectOptions.cornerSize = 12
					rectOptions.padding = 10
					rectOptions.cornerStyle = 'circle'
					rectOptions.borderDashArray = [3, 3]

					this.callSuper('initialize', rectOptions)
					this.del_img = new fabric.Image(that.del_img, {
						left: rectOptions.left + 3,
						top: rectOptions.top + 2,
						scaleX: 0.27,
						scaleY: 0.25,
						backgroundColor: 'white',
						hoverCursor: 'pointer',
						opacity: 0.8,
						selectable: false,
					})
					this.text = new fabric.Textbox(text, {
						...textOptions,
						selectable: false,
						evented: false,
						backgroundColor: 'white',
						left: this.del_img.left + this.del_img.width * this.del_img
							.scaleX + 1,
						top: rectOptions.top + 3,
						height: this.del_img.height * this.del_img.scaleY,
					})
					this.warning_border = new fabric.Rect({
						left: rectOptions.left,
						top: rectOptions.top,
						width: rectOptions.width, //矩形的宽度
						height: rectOptions.height, //矩形的高度
						stroke: 'red',
						strokeWidth: 3,
						fill: 'rgba(255, 255, 255, 0)',
						hasBorders: false,
						hasControls: false,
						selectable: false,
					})
					this.textOffsetLeft = this.text.left - this.left
					this.textOffsetTop = this.text.top - this.top
					this.delOffsetLeft = this.del_img.left - this.left
					this.delOffsetTop = this.del_img.top - this.top
					if (!rectOptions.hasTag) {
						this.show_warning()
					}
					this.on('moving', () => {
						this.recalcTextPosition()
						this.recalcDelPosition()
					})
					// this.on('rotating', () => {
					//   this.text.rotate(this.text.angle + this.angle - this._prevAngle)
					//   this.recalcTextPosition()
					//   this._prevAngle = this.angle
					// })
					this.on('added', () => {})
					this.on('scaling', (e) => {
						this.recalcTextPosition()
						this.recalcDelPosition()
					})
					this.on('removed', () => {
						if (this.isSelect) that.select_obj = ''
						this.canvas.remove(this.text)
						this.canvas.remove(this.del_img)
						this.canvas.remove(this.warning_border)
					})
					this.on('mousedown:before', () => {
						this._prevObjectStacking = this.canvas.preserveObjectStacking
						this.canvas.preserveObjectStacking = true
					})
					this.on('mouseover', function(e) {
						if (this.isSelect) return
						this.show_tag()
					})
					this.on('mouseout', function(e) {
						if (this.isSelect) return
						this.hidden_tag()
					})
					this.del_img.on('mouseover', function(e) {
						if (rect.isSelect) return
						rect.show_tag()
					})
					this.del_img.on('mouseout', function(e) {
						if (rect.isSelect) return
						rect.hidden_tag()
					})
					this.del_img.on('mousedown', function(e) {
						this.click = true
					})
					this.del_img.on('mousemove', function(e) {
						this.click = false
					})
					this.del_img.on('mouseup', function(e) {
						if (this.click) {
							that.canvas.remove(rect)
							that.changeTag = true
						}
					})
					this.on('deselected', () => {
						this.canvas.preserveObjectStacking = this._prevObjectStacking
					})
				},

				show_warning() {
					this.warning_border.set({
						left: this.left - 1,
						top: this.top - 1,
						width: this.width * this.scaleX + 2, //矩形的宽度
						height: this.height * this.scaleY + 2, //矩形的高度
					})
					that.canvas.add(this.warning_border)
					that.canvas.moveToLayer(this.warning_border, 1)
					// this.warning_border.sendBackwards(this)
					// this.warning_border.sendToBack()
					// this.warning_border.bringForward(that.img)
					that.canvas.renderAll()
				},
				hidden_warning() {
					that.canvas.remove(this.warning_border)
					that.canvas.renderAll()
				},
				show_tag(front = false) {
					if (!this.hasTag) this.text.set({
						text: '请在右侧选择或添加新标签'
					})
					that.canvas.add(this.text)
					that.canvas.add(this.del_img)
					that.canvas.moveToLayer(this.text, 99999)
					that.canvas.moveToLayer(this.del_img, 99999)

					// this.text.bringToFront()
					// this.del_img.bringToFront()
				},
				hidden_tag() {
					that.canvas.remove(this.text)
					that.canvas.remove(this.del_img)
					that.canvas.renderAll()
				},
			})
		},

	}
</script>

<style lang="scss" scoped>
	.el-container {
		flex-direction: column;
	}

	.demo {
		display: flex;
		flex-direction: column;
		align-items: center;
	}

	canvas {
		border: 1px dashed black;
	}

	.el-tag+.el-tag {
		margin-left: 10px;
	}

	.button-new-tag {
		margin-left: 10px;
		height: 32px;
		line-height: 30px;
		padding-top: 0;
		padding-bottom: 0;
	}

	.input-new-tag {
		width: 90px;
		margin-left: 10px;
		vertical-align: bottom;
	}
</style>
