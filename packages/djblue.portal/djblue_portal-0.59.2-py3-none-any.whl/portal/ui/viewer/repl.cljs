;; (ns portal.ui.viewer.repl
;;   (:require ["react" :as react]
;;             [portal.async :as a]
;;             [portal.ui.rpc :as rpc]
;;             [clojure.edn :as edn]
;;             [portal.ui.theme :as theme]
;;             [portal.ui.styled :as d]
;;             [portal.colors :as c]
;;             [portal.ui.icons :as icons]
;;             [portal.ui.inspector :as ins]))

;; (defn repl [_]
;;   (let [[history set-history!] (react/useState [])
;;         [code set-code!] (react/useState "")
;;         theme (theme/use-theme)]
;;     [ins/toggle-bg
;;      [d/div
;;       {:style {:display :flex
;;                :flex-direction :column
;;                :gap (:padding theme)}}
;;       [ins/with-key
;;        :history
;;        [ins/inspector
;;         (with-meta history {:portal.viewer/default :portal.viewer/prepl})]]
;;       [d/div
;;        {:style {:display :flex
;;                 :align-items :flex-start
;;                 :gap (:padding theme)}}
;;        [icons/chevron-right {:color (::c/tag theme)}]
;;        [d/textarea
;;         {:style {:background (ins/get-background2)
;;                  :color (::c/text theme)
;;                  :border :none
;;                  :font-family (:font-family theme)
;;                  :font-size (:font-size theme)}
;;          :style/focus {:outline :none}
;;          :value code
;;          :on-key-down
;;          (fn [e]
;;            (js/console.log e)
;;            (cond
;;              (and (= "l" (.-key e)) (.-ctrlKey e))
;;              (set-history! [])

;;              (and (= "Enter" (.-code e)) (.-ctrlKey e))
;;              (a/try
;;                (a/let [val (rpc/call 'clojure.core/eval (edn/read-string code))]
;;                  (set-history! (conj history {:tag :ret :form code :val val}))
;;                  (set-code! ""))
;;                (catch :default e
;;                  (set-history! (conj history {:tag :ret :form code :val (ex-data e) :exception true}))
;;                  (set-code! "")))))
;;          :on-change #(set-code! (.. % -target -value))}]]]]))

;; (def viewer
;;   {:component #'repl
;;    :predicate (constantly true)
;;    :name      :portal.viewer/repl})
