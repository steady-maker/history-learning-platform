import useDictStore from '@/store/modules/dict'
import { getDicts } from '@/api/system/dict/data'

/**
 * 获取字典数据
 */
export function useDict(...args) {
  const res = ref({})
  return (() => {
    args.forEach((dict_type, index) => {
      res.value[dict_type] = []
      const dicts = useDictStore().getDict(dict_type)
      if (dicts) {
        res.value[dict_type] = dicts
      } else {
        getDicts(dict_type).then(resp => {
          res.value[dict_type] = resp.data.map(p => ({ label: p.dict_label, value: p.dict_value, elTagType: p.list_class, elTagClass: p.css_class }))
          useDictStore().setDict(dict_type, res.value[dict_type])
        })
      }
    })
    return toRefs(res.value)
  })()
}