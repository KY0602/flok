<template>
  <div>
    <el-card class="box-card1" shadow="never" v-show="!noting" >
      <div slot="header" class="clearfix" v-show="!click_top_add" style="height:40px">
        <span>标签栏</span>
        <el-button @click="handleAddNote()" style="float: right" type="primary">添加标签</el-button>
      </div>
      <div slot="header" class="clearfix" v-show="click_top_add">
        <el-input v-model="input" class="note_input">
          <el-color-picker slot="prepend" size="medium" v-model="color" :predefine="predefineColors"></el-color-picker>
          <el-button slot="suffix" type="text" @click="handleConfirmNotePre()">确定</el-button>
          <el-button style="padding-right:10px;color:gray" slot="suffix" type="text" @click="click_top_add=false">取消</el-button>
        </el-input>
      </div>
        <div class="box_1">
          <div class v-for="(note,index) in note_list" :key="note.id">
            <el-input
                class="note_input"
              style="margin-bottom:5px;"
              :ref='"note_"+note.id'
              v-show="!note.is_edit"
              readonly
              v-model="note.name"
              @click.native="clickOneNote(note)"
            >
              <el-color-picker slot="prepend" size="medium" v-model="note.color" disabled ></el-color-picker>
              <i slot="suffix" class="el-input__icon el-icon-edit" @click="handleEditNote(note,index)"></i>
              <i slot="suffix" class="el-input__icon el-icon-delete" @click="handleDeleteNote(note,index)"></i>
            </el-input>
            <el-input v-show="note.is_edit" v-model="note.name" style="margin-bottom:5px;"  class="note_input">
              <el-color-picker slot="prepend" size="medium" v-model="note.color" :predefine="predefineColors" ></el-color-picker>
              <el-button slot="suffix" type="text" @click="handleConfirmNote(note,index)">确定</el-button>
              <el-button
                style="padding-right:10px;color:gray"
                slot="suffix"
                type="text"
                @click="handleCancelNote(note,index)"
              >取消</el-button>
            </el-input>
          </div>
        </div>
    </el-card>
    <div v-show="noting">
      <el-card class="box-card" shadow="never">
        <div slot="header" class="clearfix" v-show="!click_top_add" style="height:30px">
          <span>标签栏</span>
          <el-button @click="handleAddNote()" style="float: right" type="primary">添加标签</el-button>
        </div>
        <div slot="header" class="clearfix" v-show="click_top_add">
          <el-input v-model="input" class="note_input">
            <el-color-picker slot="prepend" size="medium" v-model="color" :predefine="predefineColors"></el-color-picker>
            <el-button slot="suffix" type="text" @click="handleConfirmNotePre()">确定</el-button>
            <el-button style="padding-right:10px;color:gray" slot="suffix" type="text" @click="click_top_add=false">取消</el-button>
          </el-input>
        </div>
          <div class="box_body">
            <div class v-for="(note,index) in note_list" :key="note.id">
              <el-input
                style="margin-bottom:5px"
                :ref='"note_"+note.id'
                v-show="!note.is_edit"
                readonly
                v-model="note.name"
                @click.native="clickOneNote(note)"
                class="note_input"
              >
                <el-color-picker slot="prepend" size="medium" v-model="note.color" disabled></el-color-picker>
                <i slot="suffix" class="el-input__icon el-icon-edit" @click="handleEditNote(note,index)"></i>
                <i slot="suffix" class="el-input__icon el-icon-delete" @click="handleDeleteNote(note,index)"></i>
              </el-input>
              <el-input v-show="note.is_edit" v-model="note.name" style="margin-bottom:5px">
                <el-color-picker slot="prepend" size="medium" v-model="note.color" :predefine="predefineColors" style="height: 40px"></el-color-picker>
                <el-button slot="suffix" type="text" @click="handleConfirmNote(note,index)">确定</el-button>
                <el-button
                  style="padding-right:10px;color:gray"
                  slot="suffix"
                  type="text"
                  @click="handleCancelNote(note,index)"
                >取消</el-button>
              </el-input>
            </div>
          </div>
      </el-card>

      <el-card class="box-card" style="margin-top:5px;margin-bottom:10px" shadow="never">
        <div slot="header" class="clearfix" style="height:40px">
          <span>图片列表</span>
          <el-button
            type="primary"
            @click="nextGroupImg()"
            icon="el-icon-arrow-down"
            style="float: right;margin-left:10px;margin-right:10px"
            plain
          ></el-button>
          <el-button type="primary" @click="preGroupImg()" icon="el-icon-arrow-up" style="float: right" plain></el-button>
        </div>
        <div class="box_body" >
          <el-table
            ref="picTable"
            :data="picTableData"
            :show-header="false"
            highlight-current-row
            @current-change="handleCurrentChange"
            style="width: 100%;"
            @row-click="handleRowClick"
          >
            <el-table-column property="src" label="图片" width="120">
              <template slot-scope="scope">
                <img src="./img/sound_icon.png" style="max-width:100px;height:25px;margin-bottom: 0px;" class="head_pic" />
              </template>
            </el-table-column>
            <el-table-column property="name" label="图片名"></el-table-column>
          </el-table>
        </div>
      </el-card>
    </div>
  </div>
</template>
<script>
import { alertBox } from '@/utils/alertBox.js'
import bus from './bus.js'
export default {
  name: 'NoteList',
  props: {
    noteDatasetInfo: {
      type: Object,
      default: null,
    },
    noting: {
      type: Boolean,
      default: false,
    },
  },
  data() {
    return {
      note: {
        id: '',
        color: '',
        name: '',
        is_edit: false,
      },
      total_data_num: 0,
      offset: 0,
      group_num: 8,
      show_type: '',
      input: '',
      note_list: [],
      click_top_add: false,
      color: '#409EFF',
      predefineColors: ['#ff4500', '#ff8c00', '#ffd700', '#90ee90', '#00ced1', '#1e90ff', '#c71585'],
      currentRow: null,
      picTableData: [],
      baseurl: this.$store.state.baseurl,
    }
  },
  created() {},
  mounted() {
    let that = this
    bus.$on('sendToNote', (img_info) => {
      var img_order = img_info.img_order
      this.show_type = img_info.show_type
      this.offset = img_info.img_offset
      that.getPicTableData(img_order, false, 'init', this.offset)
      //    getPicTableData(img_order, if_new_pic,direct,offset) {

      // setTimeout(function () {
      //   that.setCurrent(img_order % this.group_num)
      //   if (typeof note_id != 'undefined') that.$refs['note_' + note_id][0].focus()
      // }, 1)
    })
    bus.$on('prePicTable', (index) => {
      that.preGroupImg()
    })
    bus.$on('prePic', (index) => {
      that.setCurrent(index)
    })
    bus.$on('nextPicTable', (index) => {
      that.nextGroupImg()
    })
    bus.$on('nextPic', (index) => {
      that.setCurrent(index)
    })
    bus.$on('saveOk', (instruct) => {
      // console.log('成功接收')
      if (instruct.type === 'nextGroupImg') {
        that.nextGroupImg()
      }
      if (instruct.type === 'preGroupImg') {
        that.preGroupImg()
      }
    })
    bus.$on('saveFail', (instruct) => {
      if (instruct.type === 'changeImg') {
        that.setCurrent(instruct.args1)
      }
    })
  },
  methods: {
    getNoteList() {
      let that = this
      var data = { note_dataset_id: this.noteDatasetInfo.id }
      this.$api.data_note.get_note_list(data).then((response) => {
        if (response.data.msg === 'error') {
          alertBox(response.data.data, 'error', that, '列表加载失败')
          return
        }
        this.note_list = response.data.data
      })
    },
    getPicTableData(img_order, if_new_pic, direct, offset) {
      let that = this
      var data = {
        offset: offset,
        num: this.group_num,
        note_dataset_id: this.noteDatasetInfo.id,
        direction: direct,
        last_total_num: this.total_data_num,
      }
      if (this.show_type === 'second') data.with_note = true
      else if (this.show_type === 'third') data.with_note = false
      this.$api.data_note.get_picture_group(data).then((response) => {
        if (response.data.msg === 'error') {
          alertBox(response.data.data, 'error', that, '加载失败')
          return
        }
        that.picTableData = response.data.data
        that.total_data_num = that.picTableData[that.picTableData.length - 1].total_data_num
        that.picTableData.pop()
        that.offset = that.picTableData[0].offset
        // console.log(that.picTableData)
        // console.log(that.offset)
        let info = {}
        info.picTableData = that.picTableData
        info.if_new_pic = if_new_pic
        bus.$emit('updatePicTableData', info)
        that.setCurrent(img_order)
      })
    },
    refresh() {
      this.getNoteList()
    },
    //选中的图片行
    handleCurrentChange(val) {
      this.currentRow = val
    },
    handleRowClick(row, event, column) {
      var instruct = {}
      instruct.args1 = row
      instruct.type = 'changeImg'
      console.log(row)
      bus.$emit('savePic', instruct)
      bus.$emit('changeImage', row.name)
    },
    setCurrent(index) {
      this.$refs.picTable.setCurrentRow(this.picTableData[index])
      bus.$emit('changeImage',this.picTableData[index].name)
    },
    //预切换
    prePreGroupImg() {
      alertBox('按下了上一组按钮', 'info', this)
      var tmp = this.offset - this.group_num
      if (tmp < 0) {
        alertBox('已经是第一组', 'warning', this)
        return
      }
      var instruct = {}
      instruct.type = 'preGroupImg'
      bus.$emit('savePicsavePic', instruct)
    },
    preNextGroupImg() {
      alertBox('按下了下一组按钮', 'info', this)
      var tmp = this.offset + this.group_num
      if (tmp >= this.total_data_num) {
        alertBox('已经是最后一组', 'warning', this)
        return
      }
      var instruct = {}
      instruct.type = 'nextGroupImg'
      bus.$emit('savePic', instruct)
    },
    //下一组图片
    nextGroupImg() {
      var tmp = this.offset + this.group_num
      if (tmp >= this.total_data_num) {
        alertBox('已经是最后一组', 'warning', this)
        return
      }
      //getPicTableData(img_order, if_new_pic,direct,offset)
      this.getPicTableData(0, true, 'next', tmp)
    },
    //上一组图片
    preGroupImg() {
      var tmp = this.offset
      if (this.offset % this.group_num !== 0) {
        tmp = tmp - (this.offset % this.group_num)
      } else tmp = tmp - this.group_num
      if (tmp < 0) {
        alertBox('已经是第一组', 'warning', this)
        return
      }
      this.getPicTableData(0, true, 'pre', tmp)
    },
    handleAddNote() {
      alertBox('按下了按钮', 'info', this)
      this.click_top_add = true
      this.input = ''
    },
    handleConfirmNotePre() {
      // 检查input是否重复，检查color是否为空
      if (this.input === '' || this.color === '') {
        alertBox('不能为空', 'warning', this)
        return
      }
      let note = {
        name: this.input,
        color: this.color,
      }
      this.handleConfirmNote(note, -1)
    },
    handleConfirmNote(note, index) {
      let that = this
      console.log(note.color)
      if (note.name === '' || note.color === '' || note.color === null) {
        alertBox('不能为空', 'warning', this)
        return
      }
      if(note.name.indexOf(" ") != -1){
        alertBox('不能包含空格', 'warning', this)
        return
      }
      note.note_dataset_id = this.noteDatasetInfo.id
      var data = this.$qs.stringify(note)
      if (index === -1) {
        //添加标签
        this.$api.data_note.add_note(data).then((response) => {
          if (response.data.msg === 'error') {
            alertBox(response.data.data, 'error', that, '添加标签失败')
          } else {
            that.click_top_add = false
            that.getNoteList()
            that.$message({
              type: 'success',
              message: '添加标签成功!',
            })
          }
        })
      } else {
        //更新标签
        this.$api.data_note.edit_note(data).then((response) => {
          if (response.data.msg === 'error') {
            alertBox(response.data.data, 'error', that, '更改标签失败')
          } else {
            note.is_edit = false
            that.note_list.splice(index, 1, note)
            that.$message({
              type: 'success',
              message: '更改标签成功!',
            })
          }
        })
      }
    },
    handleCancelNote(note, index) {
      note.is_edit = false
      this.note_list.splice(index, 1, note)
    },
    handleEditNote(note, index) {
      let that = this
      alertBox('按下了编辑' + note.name, 'info', this)
      note.is_edit = true
      this.note_list.splice(index, 1, note)
    },
    handleDeleteNote(note, index) {
      let that = this
      var data = { id: note.id }
      this.$api.data_note
        .delete_note(data)
        .then(function (response) {
          if (response.data.msg === 'error') {
            alertBox(response.data.data, 'error', that, '删除失败')
          }
          that.note_list.splice(index, 1)
        })
        .catch(function (error) {
          alertBox(error, 'error', that, note.name + '删除失败')
        })
    },
    clickOneNote(note) {
		console.log(note)
      if (this.noteDatasetInfo.note_type_id === '669d056db83c4280b5a3b72d4f92be35') {
        bus.$emit('sendToClassify', note)
      } else if (this.noteDatasetInfo.note_type_id === 'a030fd61081c4f6e8acf096b5718edec') {
        bus.$emit('sendToDetection', note)
      } else if (this.noteDatasetInfo.note_type_id === '3') {
        bus.$emit('sendToSegmentation', note)
      }
    },
  },
  watch: {
    note_list(newVal) {
      this.note_list = newVal
    },
    noting(newVal) {
      this.noting = newVal
    },
    noteDatasetInfo(newVal) {
      this.noteDatasetInfo = newVal
      this.getNoteList()
    },
  },
}
</script>

<style scoped>
.text {
  font-size: 14px;
}

.item {
  margin-bottom: 18px;
}

.clearfix:before,
.clearfix:after {
  display: table;
  content: '';
}
.clearfix:after {
  clear: both;
}

.box-card {
  width: 99%;
  min-height: 100%;
  height: 100%;
}
.box_body{
    height:160px;
    overflow-y:auto;overflow-x:hidden
}
.box_1{
    height:500px;
    overflow-y:auto;overflow-x:hidden
}
.box-card1 {
  width: 99%;
  height: 600px;
}

</style>
<style>
.note_input .el-input__inner{
  height: 43px;
}
</style>


