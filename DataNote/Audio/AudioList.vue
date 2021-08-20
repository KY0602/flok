<template>
	<div class id="box">
		<el-row style="margin-bottom:30px">
			<div class="block" style="float: right">
				<el-pagination background small @size-change="handleSizeChange" @current-change="handleCurrentChange"
					:current-page="currentPage" :page-sizes="[16, 32,48]" :page-size="show_num" :pager-count="5"
					layout="total, sizes, prev, pager, next, jumper" :total="total_num"></el-pagination>
			</div>
		</el-row>
		<!-- <el-image-viewer :initial-index="view_index" v-if="showViewer" :on-close="closeViewer" :url-list="src_list" /> -->
		<!-- <el-image-viewer v-if="showViewer" :on-close="closeViewer" :url-list="[src_list]" /> -->
		<el-card :style="{display:isnone}" id="wave-card">

			<div style="position: relative;" id="waveform" ref="waveform" >
				<div id="wave-timeline" ref="wave-timeline">
				</div>
			</div>
			<!-- <div id="wave-timeline" ref="wave-timeline">
			</div>
			<div>
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
				
				
			</div> -->
			<el-button id="hide" @click="ff()">
				隐藏
			</el-button>
		</el-card>
		<el-scrollbar>
			<el-row :gutter="20">
				<el-col :span="4" v-for="item in data" :key="item.id" style="height:100px">
					<el-card :body-style="{ padding: '0px 0px' }">
						<img src="./img/sound_icon.png" style="max-width:100px;height:50px;margin-bottom: 0px;" class="head_pic" />
						<div slot="header"></div>
						
						<!-- here to fix text -->
						<span style="font-size: 15px;">{{item.name}}</span>
						<el-button size="mini" icon="el-icon-zoom-in" style="padding: 1px 1px;" type="text"
							class="button" @click="showBig(item)">试听</el-button>
						<el-button size="mini" icon="el-icon-edit-outline" style="padding: 1px 2px;" type="text"
							class="button" @click="editOne(item)">标注</el-button>
					</el-card>
				</el-col>
			</el-row>
		</el-scrollbar>
	</div>
</template>

<script>
	import WaveSurfer from 'wavesurfer.js'
	import CursorPlugin from 'wavesurfer.js/dist/plugin/wavesurfer.cursor.js'
	import Timeline from 'wavesurfer.js/dist/plugin/wavesurfer.timeline.js'

	import {
		alertBox
	} from '@/utils/alertBox.js'
	import ElImageViewer from 'element-ui/packages/image/src/image-viewer'
	import bus from './bus.js'
	export default {
		name: 'AudioList',
		components: {
			ElImageViewer
		},
		props: {
			title: {
				type: String,
				default: 'Image List',
			},
			// origin data
			show_type: {
				type: String,
				default: 'first',
			},
			noteDatasetInfo: {},
		},
		created() {
			this.currentPage = 1
		},
		data: function() {
			return {
				total_num: 0,
				total_page_num: 0,
				show_num: 16, // number of item per page
				currentPage: 1,
				data: [],
				//showViewer: false,
				waveform: null,
				// // 指定播放功能的播放时间点
				// appointTime: 1,
				// 播放倍速
				ds: 1.00,
				// // 设置音量
				// value: 0,
				isnone: "none",
				path: "",
				src_list: '',
				view_index: 0,
				baseurl: this.$store.state.baseurl,
			}
		},
		methods: {
			refresh() {
				this.getData()
			},
			getData(params = '') {
				let that = this
				if (params === '') {
					var data = {
						page: this.currentPage,
						num: this.show_num,
						note_dataset_id: this.noteDatasetInfo.id
					}
					if (this.show_type === 'second') {
						data.with_note = true
					}
					if (this.show_type === 'third') {
						data.with_note = false
					}
				} else var data = params
				console.log(data)
				this.$api.data_note.get_pictures(data).then((response) => {
					if (response.data.msg === 'error') {
						alertBox(response.data.data, 'error', that, '加载失败')
						return
					}
					that.data = response.data.data
					console.log(this.baseurl + this.data[0].src)
					that.total_num = that.data[that.data.length - 1].total_data_num
					that.total_page_num = that.data[that.data.length - 1].total_page_num
					if (that.currentPage >= that.total_page_num) that.currentPage = that.total_page_num
					that.data.pop()
				})
				console.log(this.show_type)
			},
			// 对某张图片点击了编辑
			editOne(pic) {
				console.log(pic)
				let that = this
				alertBox('开始标注', 'info', this)
				this.$emit('edit', pic)
				//跳转到mainpage处理了
			},
			//查看大图
			showBig(audio) {
				// let that = this
				// alertBox('展示大图', 'info', this)
				// this.src_list = this.baseurl + pic.src
				// document.getElementById("typediv1").style.display = "";
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
				this.path = this.baseurl + audio.src;
				this.$nextTick(() => {
					console.log(WaveSurfer)
					if (this.wavesurfer == null) {
						this.wavesurfer = WaveSurfer.create({
							// 应该在其中绘制波形的CSS选择器或HTML元素。这是唯一必需的参数。
							container: this.$refs.waveform,
							// 光标的填充颜色，指示播放头的位置。
							hideScrollbar:true,
							cursorColor: '#2C3E50',
								// 更改波形容器的背景颜色。
								backgroundColor: 'white',
								// 光标后的波形填充颜色。
								waveColor: 'blue',
								height: '100',
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
										container: '#wave-timeline',
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
					this.wavesurfer.load(this.path);
					// this.value = this.wavesurfer.getVolume() * 100
				})
				this.isnone = "";
				// this.showViewer = true
			},
			ff() {
				this.isnone = "none";
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
			// 关闭查看器
			closeViewer() {
				// this.showViewer = false
				this.isnone = "none";
			},
			// 分页
			handleSizeChange(val) {
				this.show_num = val
				if ((this.currentPage - 1) * this.show_num + 1 > this.total_num) {
					this.currentPage = Math.ceil(this.total_num / this.show_num)
				}
				this.updateDataShow()
			},
			handleCurrentChange(val) {
				this.currentPage = val
				this.updateDataShow()
			},
			updateDataShow: function() {
				this.getData()
				this.$forceUpdate()
			},
		},
		watch: {
			data: function() {},
			noteDatasetInfo(newVal) {
				this.noteDatasetInfo = newVal
				this.getData()
			},
			show_type(newVal) {
				if (newVal === 'first') {
					var params = {
						page: this.currentPage,
						num: this.show_num,
						note_dataset_id: this.noteDatasetInfo.id
					}
					this.getData(params)
				} else if (newVal === 'second') {
					var params = {
						with_note: true,
						page: this.currentPage,
						num: this.show_num,
						note_dataset_id: this.noteDatasetInfo.id,
					}
					this.getData(params)
				} else if (newVal === 'third') {
					var params = {
						with_note: false,
						page: this.currentPage,
						num: this.show_num,
						note_dataset_id: this.noteDatasetInfo.id,
					}
					this.getData(params)
				}
			},
		},
	}
</script>

<style scoped>
	.el-scrollbar {
		height: 500px;
	}

	.el-scrollbar /deep/ .el-scrollbar__wrap {
		overflow-x: hidden;
	}

	.button {
		padding: 0;
		float: right;
	}

	.image {
		width: 100%;
		display: block;
	}

	.el-card /deep/ .el-card__header {
		padding: 0px 4px;
		font-size: 14px;
	}
	
</style>
