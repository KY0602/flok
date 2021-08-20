<template>
  <el-container>
    <el-header>
      <el-row style="padding:0 0">
        <h1 style="display:inline-block;">
          {{main_info.note_type}} / {{main_info.name}}
          <i
            class="el-icon-refresh"
            circle
            @click="refresh"
            style="padding: 2px;vertical-align: center;"
          ></i>
        </h1>
      </el-row>
    </el-header>
    <el-divider></el-divider>
    <el-container>
      <el-main>
          el_main页面
      </el-main>
      <el-aside width="30%">、
          el_aside页面
      </el-aside>
    </el-container>
  </el-container>
</template>
<script>
import { alertBox } from '@/utils/alertBox.js'
import bus from '@/views/project/DataNote/bus'
export default {
  name: 'TimeSeriesDataHandler',
  components: {
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
      },
      immediate: true,
    },
  },
  data() {
    return {
      id: '',
    }
  },
  created() {
  },
  methods: {
    refresh() {
      alertBox('已刷新', 'info', this)
      this.getData(this.id)
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