<template>
  <el-container>
    <el-header>
      <el-row style="padding:0 0">
        <h1 style="display:inline-block;" v-if="!image_name">
          {{main_info.note_type}} / {{main_info.name}} / {{page_name}}
          <i
            class="el-icon-refresh"
            circle
            @click="refresh"
            style="padding: 2px;vertical-align: center;"
          ></i>
        </h1>
        <h1 style="display:inline-block;" v-if="image_name">
          <i class="el-icon-back" @click="refresh" style="border:1px;padding: 2px;vertical-align: center;"></i>
          {{main_info.note_type}} / {{main_info.name}} / {{page_name}} / {{image_name}}
        </h1>
      </el-row>
    </el-header>
    <el-divider></el-divider>
    <el-container>
      <el-main>
        <div style="position: relative" v-show="!noting">
          <el-tabs v-model="activeName" @tab-click="handleClick" style="width:100%">
            <el-tab-pane
              v-for="(item,index) in title_list"
              :key="index"
              :label="item.label+'('+item.number+')'"
              :name="item.name"
            ></el-tab-pane>
            <AudioList ref="audioList" :show_type="show_type" @edit="startNote" :noteDatasetInfo="main_info"></AudioList>
          </el-tabs>
          <el-button size="mini" @click="synchronization()" style="position: absolute;right:120px;top:5px;">
            <i class="el-icon-cloudy el-icon--left"></i>同步数据源
          </el-button>
          <el-button size="mini" @click="startNote()" style="position: absolute;right:10px;top:5px;" type="primary" plain>
            <i class="el-icon-edit-outline el-icon--left"></i>开始标注
          </el-button>
        </div>
        <!-- 下面如果改成v-if就无法监控变量 -->
        <div v-show="noting">
          <AudioClassifyPage
            v-if="main_info.note_type_id==='669d056db83c4280b5a3b72d4f92be35'"
            :noteDatasetInfo="main_info"
            ref="audioclassifyPage"
            :start_img="start_img"
          ></AudioClassifyPage>
          <AudioSegmentationPage
            v-if="main_info.note_type_id==='a030fd61081c4f6e8acf096b5718edec'"
            :noteDatasetInfo="main_info"
            ref="audiosegmentationPage"
            :start_img="start_img"
          ></AudioSegmentationPage>
        </div>
      </el-main>
      <el-aside width="30%">
        <AudioNoteList :noteDatasetInfo="main_info" ref="noteList" :noting="noting"></AudioNoteList>
      </el-aside>
    </el-container>
  </el-container>
</template>
<script>
// import DataList from "./DataList.vue";
import AudioNoteList from './AudioNoteList.vue'
import AudioClassifyPage from './AudioClassifyPage.vue'
import AudioList from './AudioList.vue'
import AudioSegmentationPage from './AudioSegmentationPage.vue'
import { alertBox } from '@/utils/alertBox.js'
import bus from '@/views/project/DataNote/bus'
export default {
  name: 'AudioHandler',
  components: {
    AudioNoteList,
    AudioClassifyPage,
    AudioList,
    AudioSegmentationPage,
  },
  props: {
    main_info: {
      type: Object,
      default: {},
    },
  },
  watch: {
    main_info: {
      handler(newVal, old) {
        this.main_info = newVal
        this.id = this.main_info.id
        this.title_list = newVal.title_list
      },
      immediate: true,
    },
  },
  data() {
    return {
      // main_info: {},
      id: '',
      noting: false,
      activeName: 'first',
      title_list: [],
      show_type: 'first',
      start_img: {},
      page_name: '全部数据',
      image_name: '',
    }
  },
  created() {
    // this.getParams()
    bus.$on('changeImage', (name) => {
      this.image_name = name
    })
  },
  mounted(){
  	  this.refresh();
  },
  methods: {
    refresh() {
      alertBox('已刷新', 'info', this)
      this.getData(this.id)
      this.$refs.audioList.refresh()
      this.$refs.noteList.refresh()
      this.noting = false
      this.activeName = 'first'
      this.show_type = 'first'
      this.page_name = '全部数据'
      this.image_name = ''
    },
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
    startNote(pic) {
      let that = this
      var data = {}
      var order = 0
	  console.log("in_audio_handler")
      console.log(pic)
      if (typeof pic != 'undefined') {
        // 点击图片
        data.data_id = pic.id
        order = pic.order
        this.image_name = pic.name
      } else {
        data.note_dataset_id = this.id
        this.activeName = 'third'
        this.show_type = 'third'
        this.page_name = '未标注数据'
      }
      data.show_type = this.show_type
	  console.log(data)
      this.$api.data_note.start_note(data).then((response) => {
        if (response.data.msg === 'error') {
          let alert_data = response.data.data
          if (alert_data.status) {
			console.log(pic)
            alertBox(alert_data.info, 'warning', that)
            this.activeName = 'first'
            this.show_type = 'first'
            this.page_name = '全部数据'
          } else {
            alertBox(alert_data.info, 'error', that, '加载失败')
          }
          return
        }
        this.start_img = response.data.data
        this.start_img.order = order
        this.noting = true
        this.image_name = this.start_img.name
		
      })
    },
    handleClick(tab, event) {
      this.show_type = tab.name
      if (this.show_type === 'first') this.page_name = '全部数据'
      if (this.show_type === 'second') this.page_name = '已标注数据'
      if (this.show_type === 'third') this.page_name = '未标注数据'
    },
    //同步
    synchronization() {
      alertBox('按下了同步按钮', 'info', this)
      var data = { id: this.id }
      this.$api.data_note.synchronization(data).then((response) => {
        if (response.data.msg === 'error') {
          alertBox(response.data.data, 'error', that, '加载失败')
          return
        }
      })
      this.refresh()
    },
  },
}
</script>

<style scoped>
.el-divider--horizontal {
  display: block;
  height: 1px;
  width: 100%;
  margin: 10px 0;
}
</style>