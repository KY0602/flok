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
      <div class="demo">
        <el-carousel
          ref="carousel"
          :initial-index="1"
          indicator-position="none"
          :autoplay="false"
          arrow="always"
          style="width:810px"
          height="460px"
          @change="preCarouselChange"
        >
          <el-carousel-item v-for="item in 3" :key="item"></el-carousel-item>
          <canvas id="canvas" :width="width" :height="height"></canvas>
        </el-carousel>
      </div>
    </div>
  </div>
</template>
<script>
import bus from './bus.js'
import { alertBox } from '@/utils/alertBox.js'

export default {
  name: 'ClassifyPage',
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
      height: 450,
      picTableData: [],
      canvas: {},
      group_num: 8,
      group_note_num:0,
      src: '',
      changeTag: false,
      current_tag: { label_id: '', name: '', color: '', content: '', id: '' },
      currentImg: {
        offset:0,
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
            offset:instruct.args1.offset,
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
              offset:instruct.args1.offset,
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
      this.canvas.clear()
      let that = this
      fabric.Image.fromURL(this.baseurl+src, function (image) {
        var tmp_w = image.width
        var tmp_h = image.height
        var xRate = that.canvas.width / image.width
        var yRate = that.canvas.height / image.height
        var setRate = xRate < yRate ? xRate : yRate
        tmp_w = tmp_w * setRate
        tmp_h = tmp_h * setRate
        var left = xRate < yRate ? 0 : (that.canvas.width - tmp_w) / 2
        var top = xRate < yRate ? (that.canvas.height - tmp_h) / 2 : 0
        image.scale(setRate)
        that.canvas.add(
          image.set({
            id: 'abc',
            left: left,
            top: top,
            selectable: false,
          })
        )
      })
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
      var data = { data_id: img_id }
      this.$api.data_note.get_note_info(data).then((response) => {
        if (response.data.msg === 'error') {
          alertBox(response.data.data, 'error', that, '列表加载失败')
          return
        }
        // console.log(response.data.data)
        var tmp = response.data.data
        if (tmp.length > 0) that.current_tag = tmp[0]
        else that.current_tag = { label_id: '', name: '', color: '', id: '' }
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
          offset:that.picTableData[0].offset,
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
    this.canvas = new fabric.Canvas('canvas', {})
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
.el-tag + .el-tag {
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
