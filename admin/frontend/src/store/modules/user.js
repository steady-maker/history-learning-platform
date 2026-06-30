import router from '@/router'
import { ElMessageBox, } from 'element-plus'
import { login, logout, getInfo } from '@/api/login'
import { getToken, setToken, removeToken } from '@/utils/auth'
import { isHttp, isEmpty } from "@/utils/validate"
import defAvaMale from '@/assets/images/man.png'
import defAvaFemale from '@/assets/images/woman.png'
const useUserStore = defineStore(
  'user',
  {
    state: () => ({
      token: getToken(),
      id: '',
      name: '',
      nickName: '',
      avatar: '',
      roles: [],
      permissions: []
    }),
    actions: {
      // 登录
      login(userInfo) {
        const username = userInfo.username.trim()
        const password = userInfo.password
        const code = userInfo.code
        const key = userInfo.key
        return new Promise((resolve, reject) => {
          login(username, password, code, key).then(res => {
            setToken(res.data.access)
            this.token = res.data.access
            resolve()
          }).catch(error => {
            reject(error)
          })
        })
      },
      // 获取用户信息
      getInfo() {
        return new Promise((resolve, reject) => {
          getInfo().then(res => {
            const user = res.user
            let avatar = user.avatar || ""
            if (!isHttp(avatar)) {
              if (isEmpty(avatar) && user.gender !== undefined) {
                if (user.gender === '0') {
                  avatar = defAvaFemale
                } else {
                  avatar = defAvaMale
                }
              } else {
                avatar = import.meta.env.VITE_APP_BASE_API + avatar
              }
            }
            if (user.roles && user.roles.length > 0) { // 验证返回的roles是否是一个非空数组
              this.roles = user.roles
              this.permissions = user.permissions
            } else {
              this.roles = ['ROLE_DEFAULT']
            }
            this.id = user.id
            this.username = user.username
            this.nickname = user.nickname
            this.dept_name = user.dept_name
            this.mobile = user.mobile
            this.email = user.email
            this.create_time = user.create_time
            this.gender = user.gender
            this.avatar = avatar
            /* 初始密码提示 */
            if(!user.pwd_update_date) {
              ElMessageBox.confirm('您的密码还是初始密码，请修改密码！',  '安全提示', {  confirmButtonText: '确定',  cancelButtonText: '取消',  type: 'warning' }).then(() => {
                router.push({ name: 'Profile', params: { activeTab: 'resetPwd' } })
              }).catch(() => {})
            }
            resolve(res)
          }).catch(error => {
            reject(error)
          })
        })
      },
      // 退出系统
      logOut() {
        return new Promise((resolve) => {
          setToken('')
          removeToken()
          resolve()
        })
      }
    }
  })

export default useUserStore
