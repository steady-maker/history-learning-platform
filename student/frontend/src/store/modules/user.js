import router from '@/router'
import { ElMessageBox, } from 'element-plus'
import { login, logout, getInfo } from '@/api/login'
import { getToken, setToken, removeToken } from '@/utils/auth'
import { isHttp, isEmpty } from "@/utils/validate"
import defAvaMale from '@/assets/images/man.png'
import defAvaFemale from '@/assets/images/woman.png'
// import { useRouter } from 'vue-router'
// const use_router = useRouter()
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
        // if(userInfo.mobile !=undefined && userInfo.mobile != '' ){
        //   const mobile = userInfo.mobile.trim()
        // }
        const code = userInfo.code
        const username = userInfo.username
        return new Promise((resolve, reject) => {
          login(userInfo).then(res => {
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
            this.mobile = user.mobile
            this.email = user.email
            this.create_time = user.create_time
            this.gender = user.gender
            this.avatar = avatar
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
          this.id = ''
          this.name = ''
          this.nickName = ''
          this.avatar = ''
          this.roles = []
          this.permissions = []
          router.push('/login')
          resolve()
        })
      }
    }
  })

export default useUserStore
