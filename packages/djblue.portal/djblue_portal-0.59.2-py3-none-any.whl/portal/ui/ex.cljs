(ns portal.ui.ex
  (:refer-clojure :exclude [Throwable->map])
  (:require
   ["sourcemapped-stacktrace" :refer [mapStackTrace]]
   [clojure.string :as str]))

(defn- ->path [file]
  (try
    (.-pathname (js/URL. file))
    (catch :default _ file)))

(defn- file->ns [file]
  (str/join
   "."
   (-> file
       (->path)
       (str/replace #"/js/" "")
       (str/split  #"\.")
       (first)
       (str/split #"/"))))

(defn- remove-ex-info-constructor
  "Including the ex-info constructor call in stack trace isn't very useful."
  [lines]
  (remove
   (comp #{'cljs.core_SLASH_cljs.core.ex_info
           'cljs.core_SLASH_new
           'cljs.core_SLASH_Function.eval}
         first)
   lines))

(defn dedupe-trace
  "Combinding two javascript exceptions via concat tends to duplicate many of
  the same lines. This may be lossy but should reduce noise overall."
  [lines]
  (with-meta
    (reverse (distinct (reverse lines)))
    (meta lines)))

(defn- ex-trace [ex]
  (try
    (let [lines (atom nil)]
      (mapStackTrace
       (.-stack ex)
       (fn [stack]
         (reset! lines stack))
       #js {:sync true})
      (prn @lines)
      (-> (for [line @lines
                :let [[_ function file-name line _column :as _trace]
                      (re-find #"\s+at (.+) \((.+):(\d+):(\d+)" line)
                      function (first (str/split function #" "))]
                :when file-name]
            [(symbol
              (munge
               (symbol (file->ns file-name)
                       (last (str/split (demunge function) #"/")))))
             (symbol (name (symbol (demunge function))))
             file-name
             (js/parseInt (or line "1"))])
          (remove-ex-info-constructor)
          (with-meta {:stack (.-stack ex)})))
    (catch :default _)))

(defn- ->class [ex]
  (let [class (.-name ex)]
    (or (not-empty class) "unknown")
    #_(try
        (let [elements (str/split class #"\$")]
          (if  (= 1 (count elements))
            (symbol class)
            (symbol
             (str/join "." (butlast elements))
             (last elements))))
        (catch :default _ (symbol class)))))

(defn- ex-chain [ex]
  (reverse (take-while some? (iterate ex-cause ex))))

(defn Throwable->map [ex]
  (let [[ex :as chain] (ex-chain ex)]
    (with-meta
      (merge
       (when-let [data (ex-data ex)]
         {:data data})
       (or (when-let [lines (seq (mapcat ex-trace chain))]
             {:trace (dedupe-trace lines)})
           {:stack (.-stack ex)})
       {:runtime :cljs
        :cause   (ex-message ex)
        :via     (mapv
                  (fn [ex]
                    (let [message (ex-message ex)]
                      (cond->
                       {:type    (->class ex)
                        :date    (ex-data ex)
                        :at      (first (ex-trace ex))}
                        message
                        (assoc :message message))))
                  chain)})
      {:portal.viewer/for
       {:stack :portal.viewer/text}})))
