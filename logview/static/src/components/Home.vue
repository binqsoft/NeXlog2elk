<template>
  <div class="flexbox column" id="main">
    <div class="flexbox toolbar center" style="background-color: rgb(33, 42, 51);">
      <div class="brand flex-item" style="color: #fff">
        <span style="font-family: Montserrat, sans-serif; font-size: 20px; color: rgb(39, 136, 187); font-weight: bold">nexpose</span>
        日志
      </div>
      <template v-for="(item, index) in indexes">
        <button class="btn" :class="{ active: currentIndex == item[0] }" @click="changeIndex(item[0])">{{ item[1] }}</button>
      </template>
      <template v-for="(item, index) in indexes">
        <select @change="onQChange" v-model="q" v-if="currentIndex == item[0] && selections[currentIndex]">
          <option value="">*</option>
          <option v-for="option in selections[currentIndex]" :value="option.value">{{option.label}}</option>
        </select>
      </template>
      <div class="flex-item flex-2 flexbox center">
        <span style="line-height: 3em; color: #fff; margin-left: 2em; margin-right: 1em">时间:</span>
        <input class="flex-item" type="date" v-model="fromDate" @change="onDateChange"/>
        <input class="flex-item" type="date" v-model="toDate" @change="onDateChange"/>
      </div>
      <input class="searchInput flex-item flex-1" @keyup.enter="search" v-model="q" placeholder="搜索"/>
      <div class="flex-item flexbox center">
        <select v-model="operate">
          <option v-if="removable" value="removeSelected">删除选中</option>
          <option value="removeAll">删除所有</option>
          <option value="backup">备份</option>
        </select>
        <button class="btn" @click="onHandleOperate">确定操作</button>
      </div>
    </div>

    <div v-if="loading" style="padding-top: 5em" class="flex-item">Loading...</div>

    <div v-if="currentIndex == 'access' && !loading" style="border: 1px solid #999" class="flex-item flexbox column table-wrapper">
      <div style="height: 40px; overflow: hidden; border-bottom: 1px solid #999;">
        <table>
        <thead>
          <tr>
            <td style="width: 50px"><input type="checkbox" :checked="selectAll" @change="onSelectAll"/></td>
            <td style="width: 200px">时间</td>
            <td>用户</td>
            <td>IP</td>
          </tr>
        </thead>
        <tbody>
          <tr v-for="item in hits" :key="item._id">
            <td><input type="checkbox"/></td>
            <td>{{ item._source.timestamp }}</td>
            <td>{{ item._source.principal }}</td>
            <td>{{ item._source.ip }}</td>
          </tr>
        </tbody>
      </table>
      </div>
      <div class="flex-item overflow">
        <table>
          <tbody>
            <template v-for="(item, index) in hits">
              <tr :key="item._id" @click="expandHit(item, index)">
                <td style="width: 50px"><input type="checkbox" :checked="item.selected" @change="onSelectItem(index, $event)"/></td>
                <td style="width: 200px">{{ item._source.timestamp }}</td>
                <td>{{ item._source.principal }}</td>
                <td>{{ item._source.ip }}</td>
              </tr>
              <tr v-if="item.expand">
                <td></td>
                <td colspan="3" style="font-size: 10px; text-align: left">{{ item._source.message }}</td>
              </tr>
            </template>
          </tbody>
        </table>
      </div>
    </div>

    <div v-if="currentIndex == 'auth' && !loading" style="border: 1px solid #999" class="flex-item flexbox column table-wrapper">
      <div style="height: 40px; overflow: hidden; border-bottom: 1px solid #999;">
        <table>
        <thead>
          <tr>
            <td style="width: 50px"><input type="checkbox" :checked="selectAll" @change="onSelectAll"/></td>
            <td style="width: 200px">时间</td>
            <td>用户</td>
            <td>操作</td>
            <td>结果</td>
            <td>原因</td>
          </tr>
        </thead>
        <tbody>
          <tr v-for="item in hits" :key="item._id">
            <td><input type="checkbox"/></td>
            <td>{{ item._source.timestamp }}</td>
            <td>{{ item._source.principal }}</td>
            <td>{{ item._source.action }}</td>
            <td>{{ item._source.actionResult }}</td>
            <td>{{ item._source.cause }}</td>

          </tr>
        </tbody>
      </table>
      </div>
      <div class="flex-item overflow">
        <table>
          <tbody>
            <template v-for="(item, index) in hits">
              <tr :key="item._id" @click="expandHit(item, index)">
                <td style="width: 50px"><input type="checkbox" :checked="item.selected" @change="onSelectItem(index, $event)"/></td>
                <td style="width: 200px">{{ item._source.timestamp }}</td>
                <td>{{ item._source.principal }}</td>
                <td>{{ item._source.action }}</td>
                <td>{{ item._source.actionResult }}</td>
                <td>{{ item._source.cause }}</td>
              </tr>
              <tr v-if="item.expand">
                <td></td>
                <td colspan="5" style="font-size: 10px; text-align: left">{{ item._source.message }}</td>
              </tr>
            </template>
          </tbody>
        </table>
      </div>
    </div>

    <div v-if="currentIndex == 'nsc' && !loading" style="border: 1px solid #999" class="flex-item flexbox column table-wrapper">
      <div style="height: 40px; overflow: hidden; border-bottom: 1px solid #999;">
        <table>
        <thead>
          <tr>
            <td style="width: 50px"><input type="checkbox" :checked="selectAll" @change="onSelectAll"/></td>
            <td style="width: 200px">时间</td>
            <td width="60">用户</td>
            <td>操作</td>
            <td>阶段</td>
          </tr>
        </thead>
        <tbody>
          <tr v-for="item in hits" :key="item._id">
            <td><input type="checkbox"/></td>
            <td>{{ item._source.timestamp }}</td>
            <td>{{ item._source.user }}</td>
            <td>{{ item._source.action }}</td>
            <td>{{ item._source.actionStage }}</td>

          </tr>
        </tbody>
      </table>
      </div>
      <div class="flex-item overflow">
        <table>
          <tbody>
            <template v-for="(item, index) in hits">
              <tr :key="item._id" @click="expandHit(item, index)">
                <td style="width: 50px"><input type="checkbox" :checked="item.selected" @change="onSelectItem(index, $event)"/></td>
                <td style="width: 200px">{{ item._source.timestamp }}</td>
                <td width="60">{{ item._source.user }}</td>
                <td>{{ item._source.action }}</td>
                <td>{{ item._source.actionStage }}</td>
              </tr>
              <tr v-if="item.expand">
                <td></td>
                <td colspan="4" style="font-size: 10px; text-align: left">{{ item._source.message }}</td>
              </tr>
            </template>
          </tbody>
        </table>
      </div>
    </div>

    <div class="bottombar flexbox table-wrapper" style="margin-top: 0; padding-top: 0">
      <div class="flex-item flex-1"> </div>
      <div class="" style="color: #fff">
        <div @click="prevPage" class="btn small"><</div>{{ offset + 50 }}/{{ total }}<div @click="nextPage" class="btn small">></div>
      </div>
    </div>
  </div>
</template>

<script>
import moment from 'moment'
export default {
  name: 'Home',
  data () {
    return {
      operate: '',
      removable: false,
      selectAll: false,
      loading: false,
      offset: 0,
      total: 0,
      currentIndex: 'access',
      indexes: [
        ['access', '访问日志'], ['auth', '授权日志'], ['nsc', '操作日志']
      ],
      msg: 'Welcome to Your Vue.js App',
      hits: [],
      q: '',
      fromDate: '',
      toDate: '',
      selections: {
        auth: [
          {label: '用户验证成功', value: "action:'Authentication attempt' AND actionResult:'succeeded'"},
          {label: '用户验证失败', value: "action:'Authentication attempt' AND actionResult:'failed'"}
        ],
        nsc: [
          {label: '用户操作', value: "action:'User'"},
          {label: '开始扫描', value: "action:'Scan' AND actionStage:'started'"},
          {label: '暂定扫描', value: "action:'Scan' AND actionStage:'paused'"},
          {label: '停止扫描', value: "action:'Scan' AND actionStage:'stopped'"}
        ]
      }
    }
  },
  created: function () {
    // `this` 指向 vm 实例
    this.loadData(this.offset)
  },

  methods: {

    loadData (offset) {
      let q = this.q
      if (this.fromDate || this.toDate) {
        if (!q) {
          q = `timestamp:[${this.fromDate || '*'} TO ${this.toDate || '*'}]`
        } else {
          q = `${q} AND timestamp:[${this.fromDate || '*'} TO ${this.toDate || '*'}]`
        }
      }
      this.loading = true
      this.selectAll = false
      fetch(`/api/nexpose-${this.currentIndex}/${offset}?q=${q}`, {
        method: 'GET',
        headers: new Headers({

        }),
        mode: 'cors',
        cache: 'default'
      }).then((response) => {
        let contentType = response.headers.get(`content-type`)
        if (contentType && contentType.includes(`application/json`)) {
          return response.json()
        }
        throw new TypeError(`Oops, we haven't got JSON!`)
      }).then((json) => {
        this.offset = offset
        this.total = json.hits.total
        this.loading = false
        this.hits = json.hits.hits.map((hit) => {
          hit._source.timestamp = moment(hit._source.timestamp).locale('zh-cn').format('llLTS')
          hit.expand = false
          hit.selected = false
          return hit
        })
      }).catch((error) => {
        console.log(error)
      })
    },

    nextPage () {
      this.loadData(Math.min(this.offset + 50, this.total))
    },
    prevPage () {
      this.loadData(Math.max(this.offset - 50, 0))
    },
    expandHit (item, index) {
      item.expand = !item.expand
      this.hits[index] = item
    },
    changeIndex (index) {
      this.currentIndex = index
      this.loadData(0)
    },
    onDateChange () {
      this.loadData(0)
    },
    onQChange () {
      this.loadData(0)
    },
    onSelectItem (index, event) {
      if (event) {
        event.stopPropagation()
        event.preventDefault()
      }
      this.hits[index].selected = !this.hits[index].selected
      this.selectAll = (this.hits.filter((hit) => hit.selected).length === this.hits.length)
      this.removable = this.hits.filter((hit) => hit.selected).length > 0
    },
    onSelectAll (e) {
      this.hits = this.hits.map((hit) => {
        hit.selected = !this.selectAll
        return hit
      })
      this.selectAll = (this.hits.filter((hit) => hit.selected).length === this.hits.length)
      this.removable = this.hits.filter((hit) => hit.selected).length > 0
    },
    onHandleOperate () {
      let q = this.q
      switch (this.operate) {
        case 'removeSelected':
          let selectedIds = this.hits.filter((hit) => hit.selected).map((hit) => `${hit._index}/${hit._type}/${hit._id}`)
          this.loading = true
          fetch(`/api/nexpose-${this.currentIndex}/remove-selected`, {
            method: 'DELETE',
            headers: new Headers({
              'Content-Type': 'application/json'
            }),
            mode: 'cors',
            cache: 'default',
            body: JSON.stringify({
              'selectedIds': selectedIds
            })
          }).then((response) => {
            let contentType = response.headers.get(`content-type`)
            if (contentType && contentType.includes(`application/json`)) {
              return response.json()
            }
            throw new TypeError(`Oops, we haven't got JSON!`)
          }).then((json) => {
            this.loadData(this.offset)
          }).catch((error) => {
            console.log(error)
          })
          break
        case 'removeAll':
          if (this.fromDate || this.toDate) {
            if (!q) {
              q = `timestamp:[${this.fromDate || '*'} TO ${this.toDate || '*'}]`
            } else {
              q = `${q} AND timestamp:[${this.fromDate || '*'} TO ${this.toDate || '*'}]`
            }
          }
          this.loading = true
          this.selectAll = false
          fetch(`/api/nexpose-${this.currentIndex}/remove-all?q=${q}`, {
            method: 'DELETE',
            headers: new Headers({}),
            mode: 'cors',
            cache: 'default'
          }).then((response) => {
            let contentType = response.headers.get(`content-type`)
            if (contentType && contentType.includes(`application/json`)) {
              return response.json()
            }
            throw new TypeError(`Oops, we haven't got JSON!`)
          }).then((json) => {
            this.loadData(this.offset)
          }).catch((error) => {
            console.log(error)
          })
          break
        case 'backup':
          if (this.fromDate || this.toDate) {
            if (!q) {
              q = `timestamp:[${this.fromDate || '*'} TO ${this.toDate || '*'}]`
            } else {
              q = `${q} AND timestamp:[${this.fromDate || '*'} TO ${this.toDate || '*'}]`
            }
          }
          window.open(`/api/nexpose-${this.currentIndex}/backup?q=${q}`, '_blank')
          break

      }
    },
    search (e) {
      this.loadData(0)
    }
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped lang="less">
  table {
    width: 100%;
    border-spacing: 0;
    border-top: 0;
    background-color: #fff;
    border-radius: 2px;
  }
  tbody tr {
    &:hover {
      background-color: #f7f8f9;
    }
  }
  td {
    border-bottom: 1px solid #f0f0f0;
    border-right: 1px solid #f0f0f0;
    padding: 0.5em;
    &:first-child {
      border-left: 1px solid #f0f0f0;
    }
  }
  input {
    line-height: 2em;
    height: 2em;
    margin-right: 1em;
    border-radius: 2px;
    border: none;
  }
  select {
    height: 2em;
    border: none;
    border-radius: 0;
    padding: 0;
    margin: 0;
    font-size: 13px;
    margin-left: 1em;
    min-width: 5em;
  }
  .generate-flex-item(@i) when (@i > 0) {
    .generate-flex-item((@i - 1));    // next iteration
    &.flex-@{i} {
      flex: @i;
    }

  }
  #main {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background-color: rgb(50, 59, 68);
  }
  .toolbar {
    height: 3em;
  }
  .table-wrapper {
    margin: 1em 2em;
  }
  .flexbox {
    display: flex;
    &.column {
      flex-direction: column;
    }
    .flex-item {
      flex: 1;
      .generate-flex-item(20);
    }
    .center {
      align-items: center;
    }
  }
  .searchInput {
    outline: none;
    padding: 0 0 0 1em;
  }

  .overflow {
    overflow: auto;
  }

  .btn {
    color: #fff;
    display: inline-block;
    background-color: rgb(43, 149, 205);
    border: 1px solid rgb(43, 149, 205);
    margin: 0.5em;
    line-height: 2em;
    border-radius: 2px;
    cursor: pointer;
    padding: 0 1em;
    &:hover {
      background-color: rgb(45, 156, 215);
    }
    &:active {
      background-color: rgb(39, 136, 187);
    }

    &.small {
      line-height: 1.5em;
    }

    &.active {
      background-color: #fff;
      color: rgb(39, 136, 187);
    }
    &[disabled] {
      border-color: #ccc;
      background-color: #ccc;
    }
  }

</style>
