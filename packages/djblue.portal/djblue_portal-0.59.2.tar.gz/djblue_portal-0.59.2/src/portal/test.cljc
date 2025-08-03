(ns portal.test
  ;; (:require [clojure.test :as test])
  ;; #?(:cljs (:require-macros portal.test))
  )

;; (def ^:private ^:dynamic *test-report* nil)

;; (defmulti ^:dynamic report (constantly :default))

;; (defn- add-method [^clojure.lang.MultiFn multifn dispatch-val f]
;;   (.addMethod multifn dispatch-val f))

;; #?(:clj
;;    (doseq [[dispatch-value f] (methods test/report)]
;;      (add-method report dispatch-value f)))

;; (defmethod report :default [message]
;;   (when *test-report*
;;     (swap! *test-report* conj message))
;;   (when-let [f (get-method report (:type message))]
;;     (f message)))

;; (defn with-report* [f]
;;   (let [test-report (atom [])]
;;     (binding [*test-report* test-report
;;               test/report (constantly nil)]
;;       #_(vary-meta (f) assoc ::report @test-report)
;;       (f))))

;; (defmacro with-report [& body] `(with-report* (fn [] ~@body)))

;; (defmacro test-ns [& args] `(with-report (test/test-ns ~@args)))