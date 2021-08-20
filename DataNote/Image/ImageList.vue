<template>
  <div class id="box">
    <el-row style="margin-bottom:10px">
      <div class="block" style="float: right">
        <el-pagination
          background
          small
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
          :current-page="currentPage"
          :page-sizes="[16, 32,48]"
          :page-size="show_num"
          :pager-count="5"
          layout="total, sizes, prev, pager, next, jumper"
          :total="total_num"
        ></el-pagination>
      </div>
    </el-row>
    <!-- <el-image-viewer :initial-index="view_index" v-if="showViewer" :on-close="closeViewer" :url-list="src_list" /> -->
    <el-image-viewer v-if="showViewer" :on-close="closeViewer" :url-list="[src_list]" />
    <el-scrollbar>
      <el-row :gutter="20">
        <el-col :span="4" v-for="item in data" :key="item.id" style="height:175px">
          <el-card :body-style="{ padding: '0px 0px' }">
            <div slot="header"></div>
            <img style="object-fit: contain;height:125px" :src="baseurl+item.src" class="image" />
            <el-button
              size="mini"
              icon="el-icon-zoom-in"
              style="padding: 1px 1px;"
              type="text"
              class="button"
              @click="showBig(item)"
            >大图</el-button>
            <el-button
              size="mini"
              icon="el-icon-edit-outline"
              style="padding: 1px 2px;"
              type="text"
              class="button"
              @click="editOne(item)"
            >标注</el-button>
          </el-card>
        </el-col>
      </el-row>
    </el-scrollbar>
  </div>
</template>

<script>
import { alertBox } from '@/utils/alertBox.js'
import ElImageViewer from 'element-ui/packages/image/src/image-viewer'

export default {
  name: 'ImageList',
  components: { ElImageViewer },
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
  data: function () {
    return {
      total_num: 0,
      total_page_num:0,
      show_num: 16, // number of item per page
      currentPage: 1,
      data: [],
      showViewer: false,
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
      if (params === ''){
        var data = { page: this.currentPage, num: this.show_num, note_dataset_id: this.noteDatasetInfo.id }
        if(this.show_type=== 'second'){
          data.with_note= true
        }
        if(this.show_type=== 'third'){
          data.with_note= false
        }
      }
      else var data = params
      this.$api.data_note.get_pictures(data).then((response) => {
        if (response.data.msg === 'error') {
          alertBox(response.data.data, 'error', that, '加载失败')
          return
        }
        that.data = response.data.data
        that.total_num = that.data[that.data.length - 1].total_data_num
        that.total_page_num = that.data[that.data.length - 1].total_page_num
        if(that.currentPage>=that.total_page_num)that.currentPage = that.total_page_num
        that.data.pop()
      })
    },
    // 对某张图片点击了编辑
    editOne(pic) {
      let that = this
      alertBox('开始标注', 'info', this)
      this.$emit('edit', pic)
      //跳转到mainpage处理了
    },
    //查看大图
    showBig(pic) {
      let that = this
      alertBox('展示大图', 'info', this)
      this.src_list = this.baseurl+pic.src
      this.showViewer = true
    },
    // 关闭查看器
    closeViewer() {
      this.showViewer = false
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
    updateDataShow: function () {
      this.getData()
      this.$forceUpdate()
    },
  },
  watch: {
    data: function () {},
    noteDatasetInfo(newVal) {
      this.noteDatasetInfo = newVal
      this.getData()
    },
    show_type(newVal) {
      if (newVal === 'first') {
        var params = { page: this.currentPage, num: this.show_num, note_dataset_id: this.noteDatasetInfo.id }
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
