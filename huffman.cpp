//#include <iostream>
//#include <string>
//#include <queue>
//#include <unordered_map>
//#include <algorithm>
//using namespace std;
//
//struct Node {
//    char ch;
//    int freq;
//    Node *left, *right;
//    Node(char c, int f) : ch(c), freq(f), left(nullptr), right(nullptr) {}
//};
//
//struct Cmp {
//    bool operator()(Node* a, Node* b) { return a->freq > b->freq; }
//};
//
//void buildCodes(Node* root, string code, unordered_map<char, string>& codes) {
//    if (!root) return;
//    if (!root->left && !root->right) {
//        codes[root->ch] = code.empty() ? "0" : code;
//        return;
//    }
//    buildCodes(root->left, code + "0", codes);
//    buildCodes(root->right, code + "1", codes);
//}
//
//void freeTree(Node* root) {
//    if (!root) return;
//    freeTree(root->left);
//    freeTree(root->right);
//    delete root;
//}
//
//int main() {
//    while (true) {
//        cout << "\n===== 哈夫曼编码/解码 =====\n";
//        cout << "1. 编码\n2. 解码\n0. 退出\n请选择: ";
//        string choice; cin >> choice;
//
//        if (choice == "1") {
//            cout << "请输入大写英文字母组成的字符串: ";
//            string s; cin >> s;
//            for (auto& c : s) c = toupper(c);
//
//            // 统计频率
//            unordered_map<char, int> freq;
//            for (char c : s) freq[c]++;
//
//            // 构建哈夫曼树
//            priority_queue<Node*, vector<Node*>, Cmp> pq;
//            for (auto& p : freq) pq.push(new Node(p.first, p.second));
//
//            while (pq.size() > 1) {
//                auto l = pq.top(); pq.pop();
//                auto r = pq.top(); pq.pop();
//                auto m = new Node(0, l->freq + r->freq);
//                m->left = l; m->right = r;
//                pq.push(m);
//            }
//            Node* root = pq.top();
//
//            // 生成编码表
//            unordered_map<char, string> codes;
//            buildCodes(root, "", codes);
//
//            // 输出编码
//            string encoded;
//            for (char c : s) encoded += codes[c];
//
//            cout << "\n字符编码表:\n";
//            for (auto& p : codes)
//                cout << "  " << p.first << ": " << p.second << "\n";
//            cout << "编码序列: " << encoded << "\n";
//            cout << "总编码长度: " << encoded.size() << " bit\n";
//
//            freeTree(root);
//
//        } else if (choice == "2") {
//            cout << "请输入参考字符串(用于重建哈夫曼树): ";
//            string s; cin >> s;
//            for (auto& c : s) c = toupper(c);
//
//            // 统计频率并建树（同上）
//            unordered_map<char, int> freq;
//            for (char c : s) freq[c]++;
//
//            priority_queue<Node*, vector<Node*>, Cmp> pq;
//            for (auto& p : freq) pq.push(new Node(p.first, p.second));
//
//            while (pq.size() > 1) {
//                auto l = pq.top(); pq.pop();
//                auto r = pq.top(); pq.pop();
//                auto m = new Node(0, l->freq + r->freq);
//                m->left = l; m->right = r;
//                pq.push(m);
//            }
//            Node* root = pq.top();
//
//            cout << "请输入待解码的二进制序列: ";
//            string bits; cin >> bits;
//
//            string decoded;
//            Node* cur = root;
//            for (char b : bits) {
//                cur = (b == '0') ? cur->left : cur->right;
//                if (!cur->left && !cur->right) {
//                    decoded += cur->ch;
//                    cur = root;
//                }
//            }
//            cout << "解码结果: " << decoded << "\n";
//
//            freeTree(root);
//
//        } else if (choice == "0") {
//            break;
//        }
//    }
//    return 0;
//}
