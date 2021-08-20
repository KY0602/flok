<template>
  <div>
    <ImageHandler
      v-if="main_info.note_dataset_type_id==='27bbe41cca3e43d1b8515b35a6ffb1ab'"
      :main_info="main_info"
      ref="imageHandler"
    ></ImageHandler>
    <TextHandler
      v-if="main_info.note_dataset_type_id==='8019768c89db461db44eb1783a3beb50'"
      :main_info="main_info"
      ref="textHandler"
    ></TextHandler>
    <VideoHandler
      v-if="main_info.note_dataset_type_id==='02217a4cf1854bf09be4237d95f83c02'"
      :main_info="main_info"
      ref="videoHandler"
    ></VideoHandler>
    <AudioHandler
      v-if="main_info.note_dataset_type_id==='4624cf7bc59c4636a89a7ee2fbfcf931'"
      :main_info="main_info"
      ref="audioHandler"
    ></AudioHandler>
    <TimeSeriesDataHandler
      v-if="main_info.note_dataset_type_id==='94c6b82e1c9340a68dd3c1ce3da03f3a'"
      :main_info="main_info"
      ref="timeSeriesDataHandler"
    ></TimeSeriesDataHandler>
  </div>
</template>
<script>
import ImageHandler from './Image/ImageHandler.vue'
import AudioHandler from './Audio/AudioHandler.vue'
import TextHandler from './Text/TextHandler.vue'
import VideoHandler from './Video/VideoHandler.vue'
import TimeSeriesDataHandler from './TimeSeriesData/TimeSeriesDataHandler.vue'

import { alertBox } from '@/utils/alertBox.js'
export default {
  name: 'dataNote',
  components: {
    ImageHandler,
    AudioHandler,
    TextHandler,
    VideoHandler,
    TimeSeriesDataHandler,
  },
  data() {
    return {
      main_info: {},
      id: '',
    }
  },
  created() {
    this.getParams()
  },
  methods: {
    getData(id) {
      //根据id获取标注集相关信息
      let that = this
      var data = { id: id }
      this.$api.data_note.query_note_dataset(data).then((response) => {
        if (response.data.msg === 'error') {
          alertBox(response.data.data, 'error', that, '加载失败')
          return
        }
        response.data.data.main_info.title_list = response.data.data.title_list
        this.main_info = response.data.data.main_info
        console.log(this.main_info)
      })
    },
    getParams() {
      // 取到路由带过来的参数
      this.id = this.$route.params.id
      this.getData(this.id)
    },
  },
}
</script>
