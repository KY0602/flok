<template>
  <div class="maintenancePlanAdd">
    <el-row>
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
          <canvas id="canvas" :width="width" :height="height" style="position: absolute; z-index: 9"></canvas>
        </el-carousel>
      </div>
    </div>
    <img src="./assets/icons/del.png" id="del_image" v-show="false" />
  </div>
</template>
<script>
import bus from './bus.js'
import { alertBox } from '@/utils/alertBox.js'

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
      width: 800,
      height: 450,
      picTableData: [],
      canvas: {},
      src: '',
      current_pos: { top: 0, left: 0, scale: 1 },
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
      this.check = false
      this.canvas.getObjects().forEach(function (item) {
        if (item.id === 'goal_obj') {
          if (!item.hasTag) {
            alertBox('请完成所有矩形框的标注', 'warning', that)
            that.check = true
            return
          }
          var info = {}
          info.content = {}
          var tmp = {}
          info.label_id = item.label_id
          tmp.top = item.top
          tmp.left = item.left
          tmp.width = item.width * item.scaleX
          tmp.height = item.height * item.scaleY
          if (tmp.top + tmp.height < that.current_pos.top) return true
          if (tmp.top > that.current_pos.top + that.current_pos.height) return true
          if (tmp.left + tmp.width < that.current_pos.left) return true
          if (tmp.left > that.current_pos.left + that.current_pos.width) return true
          if (tmp.top < that.current_pos.top) {
            let dis = that.current_pos.top - tmp.top
            tmp.height = tmp.height - dis
            tmp.top = that.current_pos.top
          }
          if (tmp.top + tmp.height > that.current_pos.top + that.current_pos.height) {
            let dis = tmp.top + tmp.height - (that.current_pos.top + that.current_pos.height)
            tmp.height = tmp.height - dis
          }
          if (tmp.left < that.current_pos.left) {
            let dis = that.current_pos.left - tmp.left
            tmp.width = tmp.width - dis
            tmp.left = that.current_pos.left
          }
          if (tmp.left + tmp.width > that.current_pos.left + that.current_pos.width) {
            let dis = tmp.left + tmp.width - (that.current_pos.left + that.current_pos.width)
            tmp.width = tmp.width - dis
          }
          tmp.top = (tmp.top - that.current_pos.top) / that.current_pos.scale
          tmp.left = (tmp.left - that.current_pos.left) / that.current_pos.scale
          tmp.width = tmp.width / that.current_pos.scale
          tmp.height = tmp.height / that.current_pos.scale

          info.content = tmp
          data.note_infos.push(info)
        }
      })
      if (that.check) return
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
      //适配大小
      this.canvas.clear()
      this.select_obj = ''
      let that = this
      fabric.Image.fromURL(this.baseurl + src, function (image) {
        var tmp_w = image.width
        var tmp_h = image.height
        var xRate = that.canvas.width / image.width
        var yRate = that.canvas.height / image.height
        var setRate = xRate < yRate ? xRate : yRate
        tmp_w = tmp_w * setRate
        tmp_h = tmp_h * setRate
        var left = xRate < yRate ? 0 : (that.canvas.width - tmp_w) / 2
        var top = xRate < yRate ? (that.canvas.height - tmp_h) / 2 : 0
        that.current_pos.left = left
        that.current_pos.top = top
        that.current_pos.scale = setRate
        that.current_pos.width = tmp_w
        that.current_pos.height = tmp_h
        image.scale(setRate)
        that.img = image
        that.canvas.add(
          image.set({
            id: 'abc',
            alt: 'xyz',
            left: left,
            top: top,
            selectable: false,
          })
        )
        that.canvas.moveToLayer(image, 0)
        // 获取标注内容
        var data = { data_id: that.currentImg.id }
        that.$api.data_note.get_note_info(data).then((response) => {
          if (response.data.msg === 'error') {
            alertBox(response.data.data, 'error', that, '列表加载失败')
            return
          }
          var tmp = response.data.data
          if (tmp.length > 0) {
            that.detail_info = tmp
            //显示标注框
            that.detail_info.forEach(function (item) {
			console.log(item)
              var pos = item.content
              pos.left = pos.left * that.current_pos.scale + that.current_pos.left
              pos.top = pos.top * that.current_pos.scale + that.current_pos.top
              pos.width = pos.width * that.current_pos.scale
              pos.height = pos.height * that.current_pos.scale
              var rectOptions = {
                hasTag: true,
                isSelect: false,
                id: 'goal_obj',
                label_id: item.label_id,
                left: pos.left,
                top: pos.top,
                width: pos.width,
                height: pos.height,
                fill: item.color,
                stroke: item.color,
              }
              var textOptions = {
                width: 0,
                fill: 'black',
                opacity: 0.8,
                fontSize: 12,
              }
              var rectWithText = new fabric.RectWithText(rectOptions, textOptions, item.name)
              that.canvas.add(rectWithText)
              rectWithText.bringForward(that.img)
            })
          } else {
            that.detail_info = []
          }
        })
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
      let index = this.currentImg.order //% this.group_num
      if (key1 === 2) {
        console.log('向右滑动，下一个图片')
        if (index === this.picTableData.length - 1) bus.$emit('nextPicTable', index)
        else {
          this.currentImg = this.picTableData[index + 1]
          this.showImage(this.currentImg.src)
          bus.$emit('nextPic', index + 1)
        }
      }
      if (key1 === 0) {
        console.log('向左滑动，上一个图片')
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
          this.mouseFrom.x < this.select_obj.left + this.select_obj.width * this.select_obj.scaleX + 20 &&
          this.mouseFrom.y > this.select_obj.top - 20 &&
          this.mouseFrom.y < this.select_obj.top + this.select_obj.height * this.select_obj.scaleY + 20
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
      return { x: mouseX / 1, y: mouseY / 1 }
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
    bus.$on('sendToDetection', (note) => {
      // console.log(note)
      if (that.select_obj !== '') {
        that.changeTag = true
        that.select_obj.hasTag = true
        that.select_obj.label_id = note.id
        that.select_obj.text.set({ text: note.name, width: 0 })
        that.select_obj.set({ fill: note.color, stroke: note.color })
        that.canvas.renderAll()
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

    fabric.Object.prototype.getZIndex = function () {
      return that.canvas.getObjects().indexOf(this)
    }

    fabric.Canvas.prototype.moveToLayer = function (object, position) {
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

      recalcTextPosition: function () {
        const sin = Math.sin(fabric.util.degreesToRadians(this.angle))
        const cos = Math.cos(fabric.util.degreesToRadians(this.angle))
        const newTop = sin * this.textOffsetLeft + cos * this.textOffsetTop
        const newLeft = cos * this.textOffsetLeft - sin * this.textOffsetTop
        const rectLeftTop = this.getPointByOrigin('left', 'top')
        this.text.set('left', rectLeftTop.x + newLeft)
        this.text.set('top', rectLeftTop.y + newTop)
      },

      recalcDelPosition: function () {
        const sin = Math.sin(fabric.util.degreesToRadians(this.angle))
        const cos = Math.cos(fabric.util.degreesToRadians(this.angle))
        const newTop = sin * this.delOffsetLeft + cos * this.delOffsetTop
        const newLeft = cos * this.delOffsetLeft - sin * this.delOffsetTop
        const rectLeftTop = this.getPointByOrigin('left', 'top')
        this.del_img.set('left', rectLeftTop.x + newLeft)
        this.del_img.set('top', rectLeftTop.y + newTop)
      },

      initialize: function (rectOptions, textOptions, text) {
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
          left: this.del_img.left + this.del_img.width * this.del_img.scaleX + 1,
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
        this.on('mouseover', function (e) {
          if (this.isSelect) return
          this.show_tag()
        })
        this.on('mouseout', function (e) {
          if (this.isSelect) return
          this.hidden_tag()
        })
        this.del_img.on('mouseover', function (e) {
          if (rect.isSelect) return
          rect.show_tag()
        })
        this.del_img.on('mouseout', function (e) {
          if (rect.isSelect) return
          rect.hidden_tag()
        })
        this.del_img.on('mousedown', function (e) {
          this.click = true
        })
        this.del_img.on('mousemove', function (e) {
          this.click = false
        })
        this.del_img.on('mouseup', function (e) {
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
        if (!this.hasTag) this.text.set({ text: '请在右侧选择或添加新标签' })
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
 