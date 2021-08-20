<template>
	<div class="maintenancePlanAdd">
		<el-row>
			<el-tag type size="medium">
				<i class="el-icon-discount" round>标注结果：</i>
			</el-tag>
			<!-- 多标签标注<el-tag
        size="medium"
        label="asa"
        :key="tag"
        v-for="tag in dynamicTags"
        closable
        :disable-transitions="false"
        @close="handleClose(tag)">
        {{tag}}
      </el-tag>-->
			<!-- 单标签标注-->
			<!-- <el-tag type size="medium" :color="current_tag.color">{{current_tag.name}}</el-tag> -->
			<el-tag type size="medium" v-if="current_tag.name">{{current_tag.name}}</el-tag>
			<el-button size="mini" style="float:right" type="primary" @click="save">保存当前标注</el-button>
		</el-row>
		<div class="panel-body" style="margin-top:20px">
			<el-card>
			<div style="position: relative;" id="waveformm" ref="waveformm" >
				<div id="wave-timelinee" ref="wave-timelinee">
				</div>
			</div>
			<div style="margin-top: 30px;">
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

			</div>
			</el-card>
			<div class="demo">
				
				<el-carousel ref="carousel" :initial-index="1" indicator-position="none" :autoplay="false"
					arrow="always" style="width:810px" height="50px" @change="preCarouselChange">
					
					
					<el-carousel-item v-for="item in 3" :key="item">
						
					</el-carousel-item>
					<!-- <canvas id="canvas" :width="width" :height="height" >
						
					</canvas> -->
					
				</el-carousel>
				<!-- <div>
					<el-button type="primary" @click="rew">后退</el-button>
					<el-button type="primary" @click="plays">
						<i class="el-icon-video-play"></i>
						播放 /
						<i class="el-icon-video-pausee"></i>
						暂停
					</el-button>
					<el-button type="primary" @click="speek">前进</el-button>
					<el-button type="primary" @click="replay">重放</el-button>
					<el-tooltip class="item" effect="dark" content="指定播放" placement="bottom">
						<el-popover placement="top" width="200" trigger="click">
							<el-input v-model="appointTime" placeholder="请输入内容" class="input-with-select">
								<el-button slot="append" @click="appointPlay">播放</el-button>
							</el-input>
							<el-button slot="reference" circle>
								指定播放
							</el-button>
						</el-popover>
					</el-tooltip>
					<span style="border: 2px solid #2f4f4f;margin-left: 8px;margin-right: 4px" />
					<el-tooltip class="item" effect="dark" content="音量" placement="bottom">
						<el-popover placement="top-start" trigger="click" style="min-width: 38px;margin-left: 10px">
							<div class="block" style="width: 42px">
								<el-slider v-model="value" vertical height="100px" @change="setVolume" />
							</div>
							<el-button slot="reference" circle>
								音量
							</el-button>
								
						</el-popover>
					</el-tooltip>
					<div style=" display: flex;">
					<img src="./img/zoom_minus.png" style="max-width:100px;height:50px;margin-right: 10px; " class="head_pic" />
					<el-tooltip content="放大缩小">
						
					<el-slider v-model="zoomval" id="zoomslider"  style="flex: 1;" class="zoomslider" @change="zzoom"/>
					
					</el-tooltip>
					<img src="./img/zoom_plus.png" style="max-width:100px;height:50px;margin-left: 10px;" class="head_pic" />
					</div> -->
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
	</div>
</template>
<script>
	import bus from './bus.js'
	import WaveSurfer from 'wavesurfer.js'
	import CursorPlugin from 'wavesurfer.js/dist/plugin/wavesurfer.cursor.js'
	import Timeline from 'wavesurfer.js/dist/plugin/wavesurfer.timeline.js'
	import {
		alertBox
	} from '@/utils/alertBox.js'

	export default {
		name: 'AudioClassifyPage',
		props: {
			noteDatasetInfo: {
				type: Object,
				default: null,
			},
			start_img: {},
		},
		data() {
			return {
				width: 800,
				height: 300,
				picTableData: [],
				// canvas: {},
				group_num: 8,
				group_note_num: 0,
				src: '',
				changeTag: false,
				waveform: null,
				// 指定播放功能的播放时间点
				appointTime: 1,
				// 播放倍速
				ds: 1.00,
				// 设置音量
				zoomval:0,
				value: 0,
				current_tag: {
					label_id: '',
					name: '',
					color: '',
					content: '',
					id: ''
				},
				currentImg: {
					offset: 0,
					order: 0,
					id: '',
					src: '',
					rel_pic_lab: [],
				},
				baseurl: this.$store.state.baseurl,
			}
		},
		watch: {
			// current_tag() {},
			// width() {
			// 	this.canvas.setWidth(this.width)
			// },
			// height() {
			// 	this.canvas.setHeight(this.height)
			// },
			noteDatasetInfo(newVal) {
				this.noteDatasetInfo = newVal
			},
			start_img(newVal) {
				console.log("start_img!")
				console.log(newVal)
				this.start_img = newVal
				this.currentImg = newVal
				this.currentImg.offset = newVal.order
				this.currentImg.order = newVal.order % this.group_num
				this.src = this.currentImg.src	
				this.showImage(this.src)
				this.getDetailInfo(newVal.id)
				this.sendToNote()
			},
		},
		methods: {
			// 保存标注
			save(instruct) {
				let that = this
				this.current_tag.content = this.current_tag.name
				this.current_tag.label_id = this.current_tag.id
				if (!this.changeTag) {
					if (instruct.type === 'carouselChange') {
						that.carouselChange(instruct.args1, instruct.args2)
					}
					if (instruct.type === 'changeImg') {
						that.currentImg = {
							offset: instruct.args1.offset,
							order: instruct.args1.order,
							id: instruct.args1.id,
							src: instruct.args1.src,
						}
						that.getDetailInfo(that.currentImg.id)
						that.showImage(that.currentImg.src)
					}
					if (instruct.type === 'preGroupImg') {
						bus.$emit('saveOk', instruct)
					}
					if (instruct.type === 'nextGroupImg') {
						bus.$emit('saveOk', instruct)
					}
					return
				}
				this.changeTag = false
				var data = {}
				data.note_infos = []
				data.note_infos.push(this.current_tag)
				data.note_infos = JSON.stringify(data.note_infos)
				data.data_id = this.currentImg.id
				data = this.$qs.stringify(data)
				//添加标签
				this.$api.data_note.save_note_info(data).then((response) => {
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
							that.carouselChange(instruct.args1, instruct.args2)
						}
						if (instruct.type === 'changeImg') {
							that.currentImg = {
								offset: instruct.args1.offset,
								order: instruct.args1.order,
								id: instruct.args1.id,
								src: instruct.args1.src,
							}
							that.getDetailInfo(that.currentImg.id)

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
			// 当前标注结果
			handleClose(tag) {
				this.dynamicTags.splice(this.dynamicTags.indexOf(tag), 1)
			},
			showImage(src) {
				// this.canvas.clear()
				let that = this
				var path = this.baseurl + src;
				// console.log(typeof(path))
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
				this.$nextTick(() => {
						console.log(WaveSurfer)
						if (this.wavesurfer == null) {
							this.wavesurfer = WaveSurfer.create({
								// 应该在其中绘制波形的CSS选择器或HTML元素。这是唯一必需的参数。
								container: document.querySelector('#waveformm'),
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
											container: '#wave-timelinee',
											formatTimeCallback: formatTimeCallback,
											timeInterval: timeInterval,
											primaryLabelInterval: primaryLabelInterval,
											secondaryLabelInterval: secondaryLabelInterval,
											primaryColor: 'blue',
											secondaryColor: 'red',
											primaryFontColor: 'blue',
											secondaryFontColor: 'red',
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
							this.wavesurfer.on('error', function(e) {
								console.warn(e);
							});
							
						}
						
						this.wavesurfer.load(path);
						// this.value = this.wavesurfer.getVolume() * 100
					})
					// this.showViewer = true
				// fabric.Image.fromURL(this.baseurl + src, function(image) {
				// 	var tmp_w = image.width
				// 	var tmp_h = image.height
				// 	var xRate = that.canvas.width / image.width
				// 	var yRate = that.canvas.height / image.height
				// 	var setRate = xRate < yRate ? xRate : yRate
				// 	tmp_w = tmp_w * setRate
				// 	tmp_h = tmp_h * setRate
				// 	var left = xRate < yRate ? 0 : (that.canvas.width - tmp_w) / 2
				// 	var top = xRate < yRate ? (that.canvas.height - tmp_h) / 2 : 0
				// 	image.scale(setRate)
				// 	that.canvas.add(
				// 		image.set({
				// 			id: 'abc',
				// 			left: left,
				// 			top: top,
				// 			selectable: false,
				// 		})
				// 	)
				// })
				
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
			zzoom(val){
				
					console.log("here")
				    this.wavesurfer.zoom(this.zoomval/0.01);
					
					console.log(this.zoomval/0.01)
			},
			preCarouselChange(key1, key2) {
				var info = {}
				info.type = 'carouselChange'
				info.args1 = key1
				info.args2 = key2
				this.save(info)
			},
			carouselChange(key1, key2) {
				// this.current_tag = { label_id: '', name: '', color: '', id: '' }
				let index = this.currentImg.order // % this.group_num
				if (key1 === 2) {
					console.log('向右滑动，下一个图片')
					if (index === this.picTableData.length - 1) bus.$emit('nextPicTable', index)
					else {
						this.currentImg = this.picTableData[index + 1]
						this.getDetailInfo(this.currentImg.id)
						this.showImage(this.currentImg.src)
						bus.$emit('nextPic', index + 1)
					}
				}
				if (key1 === 0) {
					console.log('向左滑动，上一个图片')
					if (index === 0) bus.$emit('prePicTable', index)
					else {
						this.currentImg = this.picTableData[index - 1]
						this.getDetailInfo(this.currentImg.id)
						this.showImage(this.currentImg.src)
						bus.$emit('prePic', index - 1)
					}
				}
				this.$refs.carousel.setActiveItem(1)
			},
			getDetailInfo(img_id) {
				let that = this
				var data = {
					data_id: img_id
				}
				this.$api.data_note.get_note_info(data).then((response) => {
					if (response.data.msg === 'error') {
						alertBox(response.data.data, 'error', that, '列表加载失败')
						return
					}
					// console.log(response.data.data)
					var tmp = response.data.data
					if (tmp.length > 0) that.current_tag = tmp[0]
					else that.current_tag = {
						label_id: '',
						name: '',
						color: '',
						id: ''
					}
					// console.log(that.current_tag)
				})
			},
			sendToNote() {
				// todo 高亮
				let info = {}
				info.img_offset = this.currentImg.offset
				info.img_order = this.currentImg.order
				info.show_type = this.start_img.show_type
				bus.$emit('sendToNote', info)
			},
		},
		created() {
			console.log("sdsdssdssd")
			let that = this
			bus.$on('sendToClassify', (note) => {
				that.current_tag = note
				that.current_tag.label_id = note.id
				that.changeTag = true
			})
			bus.$on('updatePicTableData', (data) => {
				that.picTableData = data.picTableData
				if (data.if_new_pic) {
					// console.log('updatePicTableData')
					//查找该图片标签等信息（详细信息）简单信息就是列表，只包括数据库单个表的信息，详细信息指的是标签等信息
					that.currentImg = {
						offset: that.picTableData[0].offset,
						order: that.picTableData[0].order,
						id: that.picTableData[0].id,
						src: that.picTableData[0].src,
					}

					that.getDetailInfo(that.currentImg.id)
					that.showImage(that.currentImg.src)
				}
			})
			bus.$on('savePic', (data) => {
				that.save(data)
			})
		},
		mounted() {
			// this.canvas = new fabric.Canvas('canvas', {})
			
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
