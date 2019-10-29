using System;
using System.Collections;
using System.Collections.Generic;
using System.Text;

namespace LeetCode{
    public class Solution3 {
        private Hashtable ht0 = new Hashtable();
        private Hashtable ht1 = new Hashtable();
        private Hashtable ht2 = new Hashtable();
        public IList<IList<int>> ThreeSum(int[] nums) {
            Array.Sort(nums);
            List<IList<int>> ret = new List<IList<int>>();
            List<int> lastList = new List<int>();
            for (int i = 0; i < nums.Length; i ++) {
                if (lastList.Count > 0 && lastList[0] == nums[i]) {
                    continue;
                }
                if (nums[i] > 0) {
                    break;
                }
                for (int j = i + 1; j < nums.Length; j ++) {
                    if (lastList.Count > 0 && lastList[0] == nums[i] && lastList[1] == nums[j]) {
                        continue;
                    }
                    if (nums[i] + nums[j] > 0) {
                        break;
                    }
                    for (int k = nums.Length - 1; k > j; k --) {
                        if (lastList.Count > 0 && lastList[0] == nums[i] && lastList[1] == nums[j] && lastList[2] == nums[k]) {
                            continue;
                        }
                        int sum = nums[i] + nums[j] + nums[k];
                        if (sum < 0) {
                            break;
                        }
                        if (sum == 0) {
                            if (lastList.Count == 0) {
                                lastList = new List<int>(){nums[i], nums[j], nums[k]};
                            }else {
                                lastList[0] = nums[i];
                                lastList[1] = nums[j];
                                lastList[2] = nums[k];
                            }
                            ret.Add(lastList);
                        }
                    }
                }
            }
            return ret;
        }

        private string getMappingVal(params int[] nums) {
            StringBuilder str = new StringBuilder();
            foreach (int n in nums) {
                str.Append(n);
            }
            return str.ToString();
        }
    }
}